"""
rebuild the in memory phase 4 caches from the database.

usage: python manage.py rebuild_search_index

ref: claude.md phase 4. resets the inverted index (lab 1), the username and
hashtag tries (lab 8 ex 3), and refreshes hashtag post_count rollups so the
next search request serves fresh data without paying the lazy hydration cost.
"""

from collections import Counter

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from algorithms.inverted_index import extract_hashtags, get_index
from algorithms.trie import get_hashtag_trie, get_user_trie

from posts.models import Post

from search.models import Hashtag, PostHashtag


class Command(BaseCommand):
    help = "rebuilds the inverted index, user trie, and hashtag trie from the db"

    def handle(self, *args, **options):
        User = get_user_model()

        # inverted index
        idx = get_index()
        idx.reset()
        idx.hydrate(Post.objects.values_list("id", "caption"))

        # user trie
        user_trie = get_user_trie()
        user_trie.reset()
        user_trie.hydrate(
            (u.lower(), uid, 1.0)
            for u, uid in User.objects.values_list("username", "id")
        )

        # hashtag trie + post_count refresh based on actual link rows
        link_counts = Counter(
            PostHashtag.objects.values_list("hashtag_id", flat=True)
        )
        with transaction.atomic():
            for tag in Hashtag.objects.all():
                count = link_counts.get(tag.id, 0)
                if tag.post_count != count:
                    Hashtag.objects.filter(id=tag.id).update(post_count=count)

        # repopulate hashtag links from caption text in case the db drifted
        for post in Post.objects.only("id", "caption"):
            for name in set(extract_hashtags(post.caption or "")):
                tag, _ = Hashtag.objects.get_or_create(name=name)
                PostHashtag.objects.get_or_create(post=post, hashtag=tag)

        # final hashtag trie hydration uses the now correct post_count
        hashtag_trie = get_hashtag_trie()
        hashtag_trie.reset()
        hashtag_trie.hydrate(
            (name, hid, float(count))
            for name, hid, count in Hashtag.objects.values_list("name", "id", "post_count")
        )

        # rewrite the on-disk snapshot so the next server boot loads this fresh
        # state instead of fast pathing through a stale pickle from a prior seed
        from search import persistence
        persistence.save_all()

        self.stdout.write(self.style.SUCCESS(
            f"rebuilt: {idx.num_documents()} docs, {idx.num_terms()} terms, "
            f"{User.objects.count()} users, {Hashtag.objects.count()} hashtags"
        ))
