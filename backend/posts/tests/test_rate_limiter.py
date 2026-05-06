"""
phase 5 follow-up: per-thread rate limiter on CommentViewSet.create.

ref: lab 4 ex 3 iterative stack ceiling. the limiter caps the number of
comments a single user can post on a single thread inside a rolling window
so a spammer cannot trip the recursive guard.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from posts.models import Post
from posts.views import RATE_LIMIT, _rate_reset

User = get_user_model()


class CommentRateLimiterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username="rl_author", password="x")
        cls.spammer = User.objects.create_user(username="rl_spammer", password="x")
        cls.post = Post.objects.create(author=cls.author, caption="tight thread")

    def setUp(self):
        _rate_reset()

    def test_429_after_limit(self):
        client = APIClient()
        client.force_authenticate(self.spammer)
        # first RATE_LIMIT comments succeed
        for i in range(RATE_LIMIT):
            r = client.post(
                "/api/posts/comments/",
                {"post": self.post.id, "content": f"msg {i}"},
                format="json",
            )
            self.assertEqual(r.status_code, 201, msg=r.content)
        # next one is blocked
        r = client.post(
            "/api/posts/comments/",
            {"post": self.post.id, "content": "one too many"},
            format="json",
        )
        self.assertEqual(r.status_code, 429)

    def test_separate_posts_have_independent_limits(self):
        other = Post.objects.create(author=self.author, caption="other thread")
        client = APIClient()
        client.force_authenticate(self.spammer)
        for i in range(RATE_LIMIT):
            client.post("/api/posts/comments/", {"post": self.post.id, "content": f"x{i}"}, format="json")
        # the limit on `self.post` should not bleed into `other`
        r = client.post(
            "/api/posts/comments/", {"post": other.id, "content": "fresh"}, format="json",
        )
        self.assertEqual(r.status_code, 201)
