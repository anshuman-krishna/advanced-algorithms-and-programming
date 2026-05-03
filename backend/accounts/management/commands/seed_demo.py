"""
seed a small demo network so the apis return non empty data.

usage: python manage.py seed_demo
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from posts.models import Comment, Like, Post
from social.models import Follow

User = get_user_model()


DEMO_USERS = [
    ("alice", "alice@example.com", "shutterbug from lisbon"),
    ("bob", "bob@example.com", "coffee and code"),
    ("carol", "carol@example.com", "trail runner"),
    ("dave", "dave@example.com", "synth nerd"),
    ("eve", "eve@example.com", "graph theory enthusiast"),
]

DEMO_POSTS = [
    ("alice", "first post on the new app"),
    ("bob", "saturday flat white"),
    ("carol", "10k splits looking decent"),
    ("alice", "lisbon at golden hour"),
    ("eve", "thinking about adjacency lists"),
]

DEMO_FOLLOWS = [
    ("alice", "bob"),
    ("alice", "carol"),
    ("bob", "alice"),
    ("bob", "eve"),
    ("carol", "alice"),
    ("dave", "alice"),
    ("dave", "bob"),
    ("eve", "alice"),
]


class Command(BaseCommand):
    help = "seeds demo users, posts, likes, comments, and follow edges."

    def handle(self, *args, **options):
        users = {}
        for username, email, bio in DEMO_USERS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": email, "bio": bio},
            )
            if created:
                user.set_password("password123")
                user.save()
            users[username] = user

        posts = []
        for author, caption in DEMO_POSTS:
            post = Post.objects.create(author=users[author], caption=caption)
            posts.append(post)

        # cross like the posts
        for post in posts:
            for username, user in users.items():
                if user.id != post.author_id:
                    Like.objects.get_or_create(user=user, post=post)

        # one parent comment plus a reply on the first post (lab 4 ex 1 shape)
        first = posts[0]
        parent = Comment.objects.create(
            post=first, author=users["bob"], content="welcome to the network"
        )
        Comment.objects.create(
            post=first, author=users["alice"], content="thanks bob", parent=parent
        )

        for follower, target in DEMO_FOLLOWS:
            Follow.objects.get_or_create(
                follower=users[follower], following=users[target]
            )

        self.stdout.write(self.style.SUCCESS(
            f"seeded {len(users)} users, {len(posts)} posts, and {Follow.objects.count()} edges"
        ))
