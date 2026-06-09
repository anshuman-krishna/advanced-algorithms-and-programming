"""
seed a rich demo network so every screen has varied, non repetitive data to
screenshot. rebuilds the demo users, posts, comments, likes, follows, hashtags,
category links, and geo coordinates each run.

usage: python manage.py seed_demo

captions carry real hashtags, so the lab 1 inverted index and the lab 8 hashtag
trie populate from the post save signal. coordinates are set per post, so the
lab 7 quadtree hydrates straight from the db. likes and posts are backdated
across the last few weeks, so the lab 8 segment tree analytics and the recency
side of the feed score both show a spread instead of one flat day.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from posts.models import Comment, CommentLike, Like, Post
from search.models import Category, PostCategory
from social.models import Follow

User = get_user_model()


# twelve distinct people so the network is not three names in a loop
DEMO_USERS = [
    ("alice", "alice@example.com", "shutterbug from lisbon"),
    ("bob", "bob@example.com", "coffee and code"),
    ("carol", "carol@example.com", "trail runner"),
    ("dave", "dave@example.com", "synth nerd"),
    ("eve", "eve@example.com", "graph theory enthusiast"),
    ("frank", "frank@example.com", "street photographer"),
    ("grace", "grace@example.com", "on device ml researcher"),
    ("heidi", "heidi@example.com", "vintage camera collector"),
    ("ivan", "ivan@example.com", "cyclist and cartographer"),
    ("judy", "judy@example.com", "live music every weekend"),
    ("mallory", "mallory@example.com", "keyboard and hardware tinkerer"),
    ("niaj", "niaj@example.com", "slow traveler, fast eater"),
]

# author, caption, location label, lat, lng, days ago, leaf category, like count.
# every city is distinct so the nearby map never stacks two pins on one spot.
DEMO_POSTS = [
    ("alice", "first light over the river #lisbon #goldenhour", "Lisbon", 38.7223, -9.1393, 24, "lisbon", 9),
    ("frank", "thrifted denim head to toe #streetwear #ootd", "Berlin", 52.5200, 13.4050, 22, "streetwear", 5),
    ("carol", "10k splits looking sharp this morning #running #trail", "Cape Town", -33.9249, 18.4241, 21, "running", 7),
    ("ivan", "century ride done, legs completely gone #cycling #roadbike", "Amsterdam", 52.3676, 4.9041, 20, "cycling", 6),
    ("grace", "new notes on attention routing #ai #ml", "Toronto", 43.6532, -79.3832, 19, "ai", 11),
    ("mallory", "soldering a keyboard pcb at 2am #hardware #mechkeys", "Austin", 30.2672, -97.7431, 18, "hardware", 4),
    ("bob", "shipped the search refactor today #software #backend", "London", 51.5074, -0.1278, 17, "software", 8),
    ("dave", "patched a fat bassline tonight #synth #modular", "Oslo", 59.9139, 10.7522, 16, "synth", 5),
    ("judy", "front row, lights everywhere #live #livemusic", "Tokyo", 35.6762, 139.6503, 15, "live", 7),
    ("heidi", "1970s rangefinder with mint glass #vintage #filmphotography", "Paris", 48.8566, 2.3522, 14, "vintage", 6),
    ("niaj", "narrow alleys at dusk #travel #kyoto", "Kyoto", 35.0116, 135.7681, 13, "tokyo", 8),
    ("alice", "sunset from the long bridge #lisbon #views", "Porto", 41.1579, -8.6291, 12, "lisbon", 10),
    ("carol", "hill repeats, lungs on fire #running #training", "Nairobi", -1.2921, 36.8219, 11, "running", 5),
    ("ivan", "coastal loop on perfect tarmac #cycling #gravel", "Barcelona", 41.3851, 2.1734, 10, "cycling", 7),
    ("grace", "tiny transformer running on device #ai #edge", "Seoul", 37.5665, 126.9780, 9, "ai", 9),
    ("bob", "flat white and pull requests #coffee #software", "Sydney", -33.8688, 151.2093, 8, "software", 6),
    ("heidi", "sunday league on a muddy pitch #football #matchday", "Manchester", 53.4808, -2.2426, 7, "football", 4),
    ("frank", "rooftop golden hour over midtown #streetphotography #goldenhour", "New York", 40.7128, -74.0060, 5, "streetwear", 8),
    ("dave", "modular patch of the week #synth #eurorack", "Reykjavik", 64.1466, -21.9426, 4, "synth", 6),
    ("judy", "synthwave night by the harbor #live #synth", "Mumbai", 19.0760, 72.8777, 3, "live", 7),
    ("niaj", "street food crawl, both hands full #travel #food", "Sao Paulo", -23.5505, -46.6333, 1, "travel", 9),
]

# leaf category to its parent. travel is a top level node with no parent.
CATEGORY_PARENT = {
    "lisbon": "travel",
    "tokyo": "travel",
    "travel": None,
    "running": "sports",
    "football": "sports",
    "cycling": "sports",
    "streetwear": "fashion",
    "vintage": "fashion",
    "ai": "tech",
    "hardware": "tech",
    "software": "tech",
    "synth": "music",
    "live": "music",
}

# two clear circles with no bridge between them, so dfs surfaces two communities
# and bfs still finds a chain inside each. mutual pairs, expanded both ways.
FOLLOW_PAIRS = [
    # circle one: photo, travel, outdoors
    ("alice", "frank"), ("alice", "heidi"), ("alice", "eve"),
    ("frank", "niaj"), ("heidi", "niaj"), ("niaj", "carol"),
    ("carol", "ivan"), ("carol", "eve"), ("ivan", "frank"),
    # circle two: tech and music
    ("bob", "grace"), ("bob", "mallory"), ("grace", "mallory"),
    ("bob", "dave"), ("dave", "judy"), ("judy", "grace"),
]

# a deep, branching thread on the first post so the thread screen shows real
# nesting and depth. (key, author, body, parent key or none).
DEMO_THREAD = [
    ("c1", "bob", "welcome to the network, this shot is unreal", None),
    ("c2", "carol", "the light is doing all the work here", None),
    ("c3", "alice", "thanks both, golden hour never misses", "c1"),
    ("c4", "frank", "what lens were you on for this?", "c1"),
    ("c5", "alice", "35mm, wide open", "c4"),
    ("c6", "frank", "clean, i might rent that one", "c5"),
    ("c7", "alice", "do it, you will not regret it", "c6"),
    ("c8", "grace", "the reflection in the water is perfect", "c2"),
    ("c9", "heidi", "reminds me of an old kodak frame", "c2"),
    ("c10", "niaj", "adding lisbon to my list right now", "c2"),
    ("c11", "bob", "you should, the trams alone are worth it", "c10"),
    ("c12", "eve", "the composition lands right on the thirds", None),
    ("c13", "dave", "agreed, the diagonal really leads the eye", "c12"),
    ("c14", "ivan", "saving this one for inspiration", "c12"),
]

# a couple of flat comments on other posts so any post you open has a thread.
DEMO_FLAT_COMMENTS = [
    (5, "bob", "on device is the whole game now"),
    (5, "mallory", "what hardware are you targeting?"),
    (9, "dave", "which venue was this?"),
    (9, "frank", "the lighting rig looks incredible"),
    (14, "carol", "that descent must have been fast"),
    (18, "alice", "the skyline at this hour is unreal"),
    (21, "judy", "now i am hungry, thanks"),
]


class Command(BaseCommand):
    help = "seeds a rich, varied demo network for screenshots and demos."

    @transaction.atomic
    def handle(self, *args, **options):
        now = timezone.now()

        users = {}
        for username, email, bio in DEMO_USERS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": email, "bio": bio},
            )
            if created:
                user.set_password("password123")
            else:
                # keep the bio fresh on a rebuild without touching the password
                user.email = email
                user.bio = bio
            user.save()
            users[username] = user

        # rebuild: clear anything these demo users owned so a re run does not
        # stack duplicate posts. deletes cascade to likes, comments, and links,
        # and the delete signals keep the search index and quadtree consistent.
        demo_ids = [u.id for u in users.values()]
        Follow.objects.filter(follower_id__in=demo_ids, following_id__in=demo_ids).delete()
        Post.objects.filter(author_id__in=demo_ids).delete()

        categories = self._ensure_categories()

        posts = []
        for row in DEMO_POSTS:
            author, caption, location, lat, lng, days_ago, leaf, like_count = row
            post = Post.objects.create(
                author=users[author],
                caption=caption,
                location=location,
                latitude=lat,
                longitude=lng,
            )
            # backdate so recency and the analytics date buckets are not all today
            created = now - timedelta(days=days_ago, hours=(post.id % 12))
            Post.objects.filter(pk=post.pk).update(created_at=created)
            post.created_at = created

            category = categories.get(leaf)
            if category is not None:
                PostCategory.objects.get_or_create(post=post, category=category)

            posts.append((post, days_ago, like_count))

        self._seed_likes(users, posts, now)
        thread_post_id = self._seed_thread(users, posts[0][0])
        self._seed_flat_comments(users, posts)
        self._seed_follows(users)

        self.stdout.write(self.style.SUCCESS(
            "seeded {u} users, {p} posts, {c} comments, {l} likes, {f} follow edges. "
            "open post {tid} on the thread tab for the deep comment tree.".format(
                u=len(users),
                p=Post.objects.filter(author_id__in=demo_ids).count(),
                c=Comment.objects.count(),
                l=Like.objects.count(),
                f=Follow.objects.filter(follower_id__in=demo_ids).count(),
                tid=thread_post_id,
            )
        ))

    def _ensure_categories(self):
        """make sure every leaf this seed references exists, with its parent.
        idempotent, so it is safe alongside seed_categories in any order."""
        nodes = {}
        # create parents first
        for leaf, parent in CATEGORY_PARENT.items():
            if parent and parent not in nodes:
                node, _ = Category.objects.get_or_create(
                    name=parent, defaults={"slug": slugify(parent)}
                )
                nodes[parent] = node
        for leaf, parent in CATEGORY_PARENT.items():
            parent_node = nodes.get(parent) if parent else None
            node, _ = Category.objects.get_or_create(
                name=leaf,
                defaults={"slug": slugify(leaf), "parent": parent_node},
            )
            nodes[leaf] = node
        return nodes

    def _seed_likes(self, users, posts, now):
        """rotate likers per post so counts vary and spread the like dates so the
        segment tree analytics shows a real distribution."""
        order = list(users.keys())
        for idx, (post, days_ago, like_count) in enumerate(posts):
            rotated = order[idx % len(order):] + order[:idx % len(order)]
            likers = [name for name in rotated if users[name].id != post.author_id]
            for j, name in enumerate(likers[:like_count]):
                like, created = Like.objects.get_or_create(user=users[name], post=post)
                if not created:
                    continue
                # walk the like back across the days since the post went up
                offset = max(0, days_ago - 1 - (j * 2) % max(1, days_ago))
                stamp = now - timedelta(days=offset, hours=(j % 9))
                Like.objects.filter(pk=like.pk).update(created_at=stamp)

    def _seed_thread(self, users, post):
        """build the deep branching thread and like a few of its comments."""
        nodes = {}
        for key, author, body, parent_key in DEMO_THREAD:
            parent = nodes.get(parent_key) if parent_key else None
            nodes[key] = Comment.objects.create(
                post=post, author=users[author], content=body, parent=parent
            )
        # spread some comment likes so total_likes aggregation is not all zeros
        comment_likes = {
            "c1": ["alice", "carol", "frank", "grace"],
            "c5": ["frank", "bob", "ivan"],
            "c8": ["alice", "heidi"],
            "c12": ["dave", "ivan", "niaj"],
            "c4": ["alice"],
        }
        for key, likers in comment_likes.items():
            for name in likers:
                CommentLike.objects.get_or_create(user=users[name], comment=nodes[key])
        return post.id

    def _seed_flat_comments(self, users, posts):
        by_index = {i + 1: post for i, (post, _, _) in enumerate(posts)}
        for one_based_index, author, body in DEMO_FLAT_COMMENTS:
            post = by_index.get(one_based_index)
            if post is None:
                continue
            Comment.objects.create(post=post, author=users[author], content=body)

    def _seed_follows(self, users):
        for follower, target in FOLLOW_PAIRS:
            Follow.objects.get_or_create(
                follower=users[follower], following=users[target]
            )
            Follow.objects.get_or_create(
                follower=users[target], following=users[follower]
            )
