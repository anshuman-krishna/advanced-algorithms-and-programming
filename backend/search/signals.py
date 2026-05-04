"""
keep the inverted index, hashtag trie, and user trie in sync with the database.
"""

from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from algorithms.inverted_index import extract_hashtags, get_index
from algorithms.trie import ensure_hashtag_trie, ensure_user_trie

from posts.models import Post

from .models import Hashtag, PostHashtag

User = get_user_model()


@receiver(post_save, sender=User)
def on_user_saved(sender, instance, created, **kwargs):
    trie = ensure_user_trie()
    trie.insert(instance.username.lower(), payload=instance.id, weight=1.0)


@receiver(post_delete, sender=User)
def on_user_deleted(sender, instance, **kwargs):
    ensure_user_trie().delete(instance.username.lower())


@receiver(post_save, sender=Post)
def on_post_saved(sender, instance, created, **kwargs):
    # full text indexing of the caption
    text = instance.caption or ""
    get_index().add_document(instance.id, text)
    _refresh_hashtag_links(instance)


@receiver(post_delete, sender=Post)
def on_post_deleted(sender, instance, **kwargs):
    get_index().remove_document(instance.id)
    # PostHashtag rows are removed via cascade. update counts.
    for tag_id in PostHashtag.objects.filter(post_id=instance.id).values_list("hashtag_id", flat=True):
        Hashtag.objects.filter(id=tag_id).update(post_count=models.F("post_count") - 1)


def _refresh_hashtag_links(post: Post) -> None:
    """resync PostHashtag rows from the caption text and bump trie weights."""
    tags = set(extract_hashtags(post.caption or ""))
    existing_links = list(post.hashtag_links.select_related("hashtag"))
    existing_names = {link.hashtag.name for link in existing_links}

    to_add = tags - existing_names
    to_remove = existing_names - tags

    with transaction.atomic():
        for name in to_add:
            tag, _ = Hashtag.objects.get_or_create(name=name)
            PostHashtag.objects.get_or_create(post=post, hashtag=tag)
            Hashtag.objects.filter(id=tag.id).update(post_count=tag.post_count + 1)
            ensure_hashtag_trie().insert(name, payload=tag.id, weight=float(tag.post_count + 1))
        for name in to_remove:
            tag = Hashtag.objects.filter(name=name).first()
            if tag is None:
                continue
            PostHashtag.objects.filter(post=post, hashtag=tag).delete()
            new_count = max(0, tag.post_count - 1)
            Hashtag.objects.filter(id=tag.id).update(post_count=new_count)
            if new_count == 0:
                ensure_hashtag_trie().delete(name)
            else:
                ensure_hashtag_trie().insert(name, payload=tag.id, weight=float(new_count))
