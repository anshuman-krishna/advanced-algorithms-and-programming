"""
seed a rich pet themed demo network so every screen has varied, non repetitive
data to screenshot. rebuilds the demo users, posts, comments, likes, follows,
hashtags, category links, notifications, and pet photos each run.

usage: python manage.py seed_demo

captions carry real hashtags, so the lab 1 inverted index and the lab 8 hashtag
trie populate from the post save signal. coordinates are set per post, so the
lab 7 quadtree hydrates straight from the db. each post points at a stable cat or
dog photo that matches the account, so the feed shows real images. likes and posts
are backdated across the last few weeks, so the lab 8 segment tree analytics and
the recency side of the feed score both show a spread instead of one flat day.
notifications are seeded directly so the activity inbox is rich the moment you log
in, without waiting on a queue drain.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from notifications.models import Notification
from posts.models import Comment, CommentLike, Like, Post
from posts.pet_images import species_image
from search.models import Category, PostCategory
from social.models import Follow

User = get_user_model()


# username, email, bio, species. the species decides whether the account gets
# cat or dog photos so a post never mismatches its caption.
DEMO_USERS = [
    ("alice", "alice@example.com", "cat mom · luna the tuxedo", "cat"),
    ("bob", "bob@example.com", "dog dad · max the golden", "dog"),
    ("carol", "carol@example.com", "trail dog · scout the beagle", "dog"),
    ("dave", "dave@example.com", "cats and synths · mochi the ragdoll", "cat"),
    ("eve", "eve@example.com", "graphs and a black cat · shadow", "cat"),
    ("frank", "frank@example.com", "street dog photos · rufus the rescue", "dog"),
    ("grace", "grace@example.com", "ml researcher · clementine the tabby", "cat"),
    ("heidi", "heidi@example.com", "vintage cams · willow the calico", "cat"),
    ("ivan", "ivan@example.com", "cyclist and a corgi · biscuit", "dog"),
    ("judy", "judy@example.com", "live music and a husky · pepper", "dog"),
    ("mallory", "mallory@example.com", "keyboards and a kitten · tofu", "cat"),
    ("niaj", "niaj@example.com", "slow travels with daisy the doodle", "dog"),
    # studio crew, a third community
    ("quinn", "quinn@example.com", "film photos · pixel the siamese", "cat"),
    ("ravi", "ravi@example.com", "street food and ladoo the beagle", "dog"),
    ("stan", "stan@example.com", "darkroom prints · marble the maine coon", "cat"),
    ("tara", "tara@example.com", "runner with comet the vizsla", "dog"),
    # two loose pairs, good targets for following someone by hand
    ("uma", "uma@example.com", "potter · clay the persian", "cat"),
    ("wendy", "wendy@example.com", "baker · yeast the sphynx", "cat"),
    ("victor", "victor@example.com", "van life with two huskies", "dog"),
    ("xena", "xena@example.com", "agility trials · flash the border collie", "dog"),
]

# author, caption, location, lat, lng, days ago, leaf category, like count.
# every city is distinct so the nearby map never stacks two pins on one spot.
DEMO_POSTS = [
    ("alice", "luna found the one sunbeam in the house #catsofinstagram #tuxedocat", "Lisbon", 38.7223, -9.1393, 24, "tabby", 9),
    ("bob", "max says the ball is non negotiable #dogsofinstagram #goldenretriever", "London", 51.5074, -0.1278, 22, "retriever", 8),
    ("grace", "clementine supervising the code review #tabbycat #catnap", "Toronto", 43.6532, -79.3832, 21, "tabby", 11),
    ("carol", "scout did the whole trail and asked for more #beagle #traildog", "Cape Town", -33.9249, 18.4241, 20, "hikes", 7),
    ("dave", "mochi versus the new modular patch, mochi won #ragdoll #kitten", "Oslo", 59.9139, 10.7522, 19, "ragdoll", 6),
    ("frank", "rufus on the rooftop at golden hour #rescuedog #streetdog", "New York", 40.7128, -74.0060, 18, "adoptable", 8),
    ("heidi", "willow claimed the camera bag again #calico #catsofinsta", "Paris", 48.8566, 2.3522, 17, "ragdoll", 6),
    ("ivan", "biscuit, short legs and a long ride #corgi #bikedog", "Amsterdam", 52.3676, 4.9041, 16, "puppies", 7),
    ("eve", "shadow doing midnight zoomies, again #blackcat #zoomies", "Berlin", 52.5200, 13.4050, 15, "kittens", 9),
    ("judy", "pepper sang along at soundcheck #husky #huskytalks", "Tokyo", 35.6762, 139.6503, 14, "husky", 7),
    ("mallory", "tofu testing every keycap by sitting on it #kitten #catsofinstagram", "Austin", 30.2672, -97.7431, 13, "kittens", 5),
    ("niaj", "daisy made friends at every street stall #goldendoodle #travelpup", "Sao Paulo", -23.5505, -46.6333, 12, "retriever", 9),
    ("alice", "bath day for luna, mixed reviews #tuxedocat #bathtime", "Porto", 41.1579, -8.6291, 11, "bathtime", 10),
    ("carol", "scout post run nap, fully earned #beagle #tiredpup", "Nairobi", -1.2921, 36.8219, 10, "hikes", 5),
    ("grace", "clementine and the warm laptop, a love story #tabbycat #catlife", "Seoul", 37.5665, 126.9780, 9, "tabby", 9),
    ("bob", "max at the dog park making the rounds #goldenretriever #dogpark", "Sydney", -33.8688, 151.2093, 8, "retriever", 6),
    ("frank", "rufus adoption day throwback #adoptdontshop #rescue", "Manchester", 53.4808, -2.2426, 7, "adoptable", 8),
    ("dave", "mochi loaf achieved peak fluff #ragdoll #catloaf", "Reykjavik", 64.1466, -21.9426, 5, "ragdoll", 7),
    ("judy", "pepper beach day, sand absolutely everywhere #husky #beachday", "Mumbai", 19.0760, 72.8777, 4, "beachday", 7),
    ("heidi", "willow got a haircut and is very judgmental about it #calico #groomday", "Kyoto", 35.0116, 135.7681, 3, "haircuts", 6),
    ("niaj", "daisy is fostering two pups this week #fosterdog #adoptable", "Barcelona", 41.3851, 2.1734, 1, "fosters", 9),
    # studio crew posts
    ("quinn", "pixel judging my latest film scans #catsofinstagram #siamese", "Madrid", 40.4168, -3.7038, 23, "tabby", 8),
    ("ravi", "ladoo waiting outside the dosa stall #dogsofinstagram #beagle", "Chennai", 13.0827, 80.2707, 21, "puppies", 7),
    ("stan", "marble the maine coon, all sixteen pounds of him #mainecoon #catsofinsta", "Rome", 41.9028, 12.4964, 20, "ragdoll", 9),
    ("tara", "comet finished the ten k with me #vizsla #rundog", "Dublin", 53.3498, -6.2603, 18, "hikes", 6),
    ("quinn", "darkroom buddy clocked in for the night #siamese #filmphotography", "Vienna", 48.2082, 16.3738, 15, "tabby", 7),
    ("ravi", "ladoo got the last bite, fair enough #beagle #foodie", "Prague", 50.0755, 14.4378, 13, "retriever", 8),
    ("stan", "marble versus the cardboard box, the box lost #mainecoon #catloaf", "Helsinki", 60.1699, 24.9384, 11, "ragdoll", 6),
    ("tara", "comet trail selfie, ears fully up #vizsla #traildog", "Edinburgh", 55.9533, -3.1883, 9, "hikes", 7),
    # loose pair posts
    ("uma", "clay the persian inspecting the fresh mugs #persiancat #pottery", "Valencia", 39.4699, -0.3763, 16, "kittens", 6),
    ("wendy", "yeast the sphynx supervising the sourdough #sphynx #baking", "Copenhagen", 55.6761, 12.5683, 12, "kittens", 7),
    ("victor", "two huskies, one tiny van, zero regrets #husky #vanlife", "Bergen", 60.3913, 5.3221, 10, "husky", 8),
    ("xena", "flash cleared the weave poles clean #bordercollie #agility", "Wellington", -41.2865, 174.7762, 6, "puppies", 9),
    # a few fresh ones from the original crew so the top of the feed feels active
    ("bob", "max made a new friend at the cafe #goldenretriever #dogfriends", "Singapore", 1.3521, 103.8198, 5, "retriever", 7),
    ("grace", "clementine and the second monitor life #tabbycat #wfh", "Bangkok", 13.7563, 100.5018, 4, "tabby", 8),
    ("frank", "rufus golden hour, part two #rescuedog #goldenhour", "Mexico City", 19.4326, -99.1332, 2, "adoptable", 9),
    ("niaj", "daisy says goodnight from the hostel #goldendoodle #travelpup", "Vancouver", 49.2827, -123.1207, 1, "fosters", 8),
]

# leaf category to its parent, mirrors seed_categories so the explore tree lines up
CATEGORY_PARENT = {
    "kittens": "cats", "tabby": "cats", "ragdoll": "cats",
    "puppies": "dogs", "retriever": "dogs", "husky": "dogs",
    "adoptable": "rescue", "fosters": "rescue",
    "bathtime": "grooming", "haircuts": "grooming",
    "hikes": "outdoors", "beachday": "outdoors",
}

# three clear circles plus two loose pairs, so dfs surfaces several communities
# and bfs still finds a chain inside each. pairs are seeded both ways so the
# undirected friendship view treats them as mutual.
FOLLOW_PAIRS = [
    # cat crew
    ("alice", "dave"), ("alice", "eve"), ("alice", "grace"),
    ("dave", "grace"), ("eve", "heidi"), ("grace", "mallory"), ("heidi", "mallory"),
    # dog park
    ("bob", "carol"), ("bob", "frank"), ("bob", "niaj"),
    ("carol", "ivan"), ("frank", "judy"), ("ivan", "niaj"), ("judy", "niaj"),
    # studio crew
    ("quinn", "ravi"), ("quinn", "stan"), ("ravi", "tara"), ("stan", "tara"),
    # two loose pairs
    ("uma", "wendy"),
    ("victor", "xena"),
]

# a deep, branching thread on the first post so the thread screen shows real
# nesting and depth. (key, author, body, parent key or none).
DEMO_THREAD = [
    ("c1", "bob", "luna owning that sunbeam, iconic", None),
    ("c2", "grace", "clementine would fight her for it", None),
    ("c3", "alice", "she guards that spot like it is a job", "c1"),
    ("c4", "frank", "what breed is luna, that coat is unreal", "c1"),
    ("c5", "alice", "tuxedo, full formal wear at all times", "c4"),
    ("c6", "bob", "max would just lie on top of her", "c5"),
    ("c7", "alice", "luna would absolutely not allow that", "c6"),
    ("c8", "heidi", "willow approves of this nap form", "c2"),
    ("c9", "eve", "shadow says hello from the dark side", "c2"),
    ("c10", "niaj", "daisy wants to be friends with everyone here", "c2"),
    ("c11", "dave", "mochi is also a professional sunbather", "c10"),
    ("c12", "ivan", "biscuit naps exactly like this, legs out", None),
    ("c13", "mallory", "tofu is taking detailed notes", "c12"),
    ("c14", "judy", "pepper would just howl at the sunbeam", "c12"),
]

# flat comments on other posts so any post you open already has a thread.
# index is one based into DEMO_POSTS.
DEMO_FLAT_COMMENTS = [
    (2, "alice", "max is the goodest boy, no notes"),
    (2, "grace", "that face deserves the ball"),
    (3, "bob", "clementine is so judgmental and i love it"),
    (5, "eve", "mochi the synth tester, a legend"),
    (8, "carol", "biscuit nation rise up"),
    (8, "judy", "those legs are everything"),
    (9, "alice", "shadow and luna would be zoomie partners"),
    (12, "frank", "daisy is pure joy in dog form"),
    (16, "niaj", "dog park royalty right there"),
    (17, "carol", "throwback adoption posts get me every time"),
    (22, "alice", "pixel has the best resting judge face"),
    (23, "tara", "ladoo deserves the whole dosa honestly"),
    (24, "quinn", "marble is basically a small lion"),
    (26, "stan", "the darkroom cat union approves"),
    (30, "wendy", "clay supervising quality control, respect"),
    (33, "victor", "flash is faster than my two combined"),
    (34, "frank", "cafe dogs making friends, the dream"),
    (36, "grace", "golden hour rufus never misses"),
]

# recipient, actor, kind, post index (one based into DEMO_POSTS or none),
# comment key (or none), is_priority, is_read, hours ago. seeded straight into
# the table so the inbox is full the moment alice (or bob, grace) logs in.
DEMO_NOTIFICATIONS = [
    ("alice", "mallory", "comment", 13, None, False, False, 2),
    ("alice", "bob", "like", 1, None, False, False, 3),
    ("alice", "grace", "comment", 1, "c2", False, False, 5),
    ("alice", "bob", "reply", 1, "c6", True, False, 7),
    ("alice", "dave", "follow", None, None, False, False, 9),
    ("alice", "niaj", "like", 13, None, False, True, 26),
    ("alice", "frank", "comment", 1, "c4", False, True, 30),
    ("alice", "grace", "like", 1, None, False, True, 40),
    ("alice", "heidi", "follow", None, None, False, True, 50),
    ("alice", "eve", "like", 13, None, False, True, 62),
    ("bob", "alice", "like", 2, None, False, False, 4),
    ("bob", "grace", "comment", 2, None, False, False, 8),
    ("bob", "carol", "follow", None, None, False, True, 28),
    ("grace", "mallory", "comment", 3, None, True, False, 1),
    ("grace", "alice", "like", 3, None, False, False, 6),
    ("grace", "dave", "follow", None, None, False, False, 12),
]


class Command(BaseCommand):
    help = "seeds a rich, pet themed demo network for screenshots and demos."

    @transaction.atomic
    def handle(self, *args, **options):
        now = timezone.now()

        users = {}
        species = {}
        for username, email, bio, kind in DEMO_USERS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": email, "bio": bio},
            )
            if created:
                user.set_password("password123")
            else:
                user.email = email
                user.bio = bio
                user.set_password("password123")
            user.save()
            users[username] = user
            species[username] = kind

        # rebuild: clear anything these demo users owned so a re run does not
        # stack duplicate posts. deletes cascade to likes, comments, and links,
        # and the delete signals keep the search index and quadtree consistent.
        demo_ids = [u.id for u in users.values()]
        Notification.objects.filter(recipient_id__in=demo_ids).delete()
        Follow.objects.filter(follower_id__in=demo_ids, following_id__in=demo_ids).delete()
        Post.objects.filter(author_id__in=demo_ids).delete()

        categories = self._ensure_categories()

        # per species counter so each post gets the next photo from its pool
        photo_idx = {"cat": 0, "dog": 0}
        posts = []
        for row in DEMO_POSTS:
            author, caption, location, lat, lng, days_ago, leaf, like_count = row
            kind = species[author]
            post = Post.objects.create(
                author=users[author],
                caption=caption,
                location=location,
                latitude=lat,
                longitude=lng,
                image_url=species_image(kind, photo_idx[kind]),
            )
            photo_idx[kind] += 1

            created = now - timedelta(days=days_ago, hours=(post.id % 12))
            Post.objects.filter(pk=post.pk).update(created_at=created)
            post.created_at = created

            category = categories.get(leaf)
            if category is not None:
                PostCategory.objects.get_or_create(post=post, category=category)

            posts.append((post, days_ago, like_count))

        post_objs = [p for (p, _, _) in posts]
        self._seed_likes(users, posts, now)
        thread_post_id, thread_nodes = self._seed_thread(users, posts[0][0])
        self._seed_flat_comments(users, posts)
        self._seed_follows(users)
        self._seed_notifications(users, post_objs, thread_nodes, now)

        self.stdout.write(self.style.SUCCESS(
            "seeded {u} users, {p} posts, {c} comments, {l} likes, {f} follow edges, "
            "{n} notifications. open post {tid} on the thread tab for the deep "
            "comment tree.".format(
                u=len(users),
                p=Post.objects.filter(author_id__in=demo_ids).count(),
                c=Comment.objects.count(),
                l=Like.objects.count(),
                f=Follow.objects.filter(follower_id__in=demo_ids).count(),
                n=Notification.objects.count(),
                tid=thread_post_id,
            )
        ))

    def _ensure_categories(self):
        """make sure every leaf this seed references exists, with its parent.
        idempotent, so it is safe alongside seed_categories in any order."""
        nodes = {}
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
                offset = max(0, days_ago - 1 - (j * 2) % max(1, days_ago))
                stamp = now - timedelta(days=offset, hours=(j % 9))
                Like.objects.filter(pk=like.pk).update(created_at=stamp)

    def _seed_thread(self, users, post):
        """build the deep branching thread and like a few of its comments.
        returns the post id and the key -> comment node map so the notification
        seeder can point at real comment ids."""
        nodes = {}
        for key, author, body, parent_key in DEMO_THREAD:
            parent = nodes.get(parent_key) if parent_key else None
            nodes[key] = Comment.objects.create(
                post=post, author=users[author], content=body, parent=parent
            )
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
        return post.id, nodes

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

    def _seed_notifications(self, users, post_objs, thread_nodes, now):
        """write notification rows straight to the table so the inbox is full
        immediately. ref: lab 3 ex 2 produces these the same way at runtime, this
        just pre populates them for the demo."""
        for recipient, actor, kind, post_idx, comment_key, prio, read, hours in DEMO_NOTIFICATIONS:
            if recipient not in users or actor not in users:
                continue
            post_id = None
            if post_idx is not None and 1 <= post_idx <= len(post_objs):
                post_id = post_objs[post_idx - 1].id
            comment_id = None
            if comment_key is not None and comment_key in thread_nodes:
                comment_id = thread_nodes[comment_key].id
                if post_id is None:
                    post_id = thread_nodes[comment_key].post_id
            n = Notification.objects.create(
                recipient=users[recipient],
                actor=users[actor],
                kind=kind,
                post_id=post_id,
                comment_id=comment_id,
                is_priority=prio,
                is_read=read,
                delivered_at=now,
            )
            stamp = now - timedelta(hours=hours)
            Notification.objects.filter(pk=n.pk).update(created_at=stamp)
