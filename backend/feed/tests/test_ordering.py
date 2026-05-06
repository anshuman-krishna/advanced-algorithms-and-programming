"""
phase 3 + phase 5 + follow-up: assert that the home feed orders posts by the
weighted (0.7 likes + 0.3 recency) score after passing through the lab 3 ex 3
priority queue, and that the trending heap picks the top-k by the same score.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from posts.models import Like, Post
from feed.services import build_home_feed, build_trending_feed
from social.models import Follow

User = get_user_model()


class FeedOrderingIntegrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.viewer = User.objects.create_user(username="viewer", password="x")
        cls.author = User.objects.create_user(username="author", password="x")
        Follow.objects.create(follower=cls.viewer, following=cls.author)
        now = timezone.now()
        # three posts: fresh + low likes, fresh + high likes, old + high likes
        cls.fresh_low = Post.objects.create(author=cls.author, caption="fresh low")
        cls.fresh_high = Post.objects.create(author=cls.author, caption="fresh high")
        cls.old_high = Post.objects.create(author=cls.author, caption="old high")
        Post.objects.filter(pk=cls.old_high.pk).update(created_at=now - timedelta(hours=48))
        # add likes
        for u in range(2):
            User.objects.create_user(username=f"liker{u}", password="x")
        likers = list(User.objects.filter(username__startswith="liker"))
        Like.objects.create(user=likers[0], post=cls.fresh_low)
        for liker in likers:
            Like.objects.create(user=liker, post=cls.fresh_high)
            Like.objects.create(user=liker, post=cls.old_high)

    def setUp(self):
        from algorithms.follow_graph import _graph
        _graph.reset()

    def test_home_feed_orders_by_score_breakdown(self):
        feed = build_home_feed(self.viewer.id, limit=10)
        ids = [item["post_id"] for item in feed]
        # fresh_high must outrank old_high since recency contributes
        self.assertLess(ids.index(self.fresh_high.id), ids.index(self.old_high.id))

    def test_home_feed_payload_includes_score_breakdown(self):
        feed = build_home_feed(self.viewer.id, limit=1)
        breakdown = feed[0]["score_breakdown"]
        for key in ("likes_normalized", "likes_contribution",
                    "recency_factor", "recency_contribution", "total"):
            self.assertIn(key, breakdown)

    def test_trending_picks_top_k(self):
        from algorithms.max_heap import mark_dirty

        mark_dirty()
        top = build_trending_feed(k=2, force=True)
        self.assertEqual(len(top), 2)
        # both fresh_high and old_high should be present (2 likes each, fresh wins)
        ids = [t["post_id"] for t in top]
        self.assertIn(self.fresh_high.id, ids)
