"""
phase 4 + 5 follow-up: assert that the lab 5 generalized tree post counts roll
up correctly through `post_order_aggregate` after we attach posts to leaf
categories.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Like, Post
from search.models import Category, PostCategory
from search.services import category_engagement, explore_tree

User = get_user_model()


class ExploreTreeIntegrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="explorer", password="x")
        # build a small two level taxonomy by hand using slugs that cannot
        # collide with the seeded production taxonomy
        cls.tech_root = Category.objects.create(name="tech-iso", slug="tech-iso")
        cls.ai = Category.objects.create(name="ai-iso", slug="ai-iso", parent=cls.tech_root)
        cls.hardware = Category.objects.create(
            name="hardware-iso", slug="hardware-iso", parent=cls.tech_root,
        )

        # one post under ai, two under hardware
        cls.p1 = Post.objects.create(author=cls.user, caption="ai post")
        cls.p2 = Post.objects.create(author=cls.user, caption="cpu post")
        cls.p3 = Post.objects.create(author=cls.user, caption="gpu post")
        PostCategory.objects.create(post=cls.p1, category=cls.ai)
        PostCategory.objects.create(post=cls.p2, category=cls.hardware)
        PostCategory.objects.create(post=cls.p3, category=cls.hardware)

        # add a couple likes so engagement is non-zero
        liker = User.objects.create_user(username="liker", password="x")
        Like.objects.create(user=liker, post=cls.p1)
        Like.objects.create(user=liker, post=cls.p2)

    def test_post_counts_roll_up_to_root(self):
        tree = explore_tree()
        # walk the returned tree dict and find our isolated tech node
        tech_payload = _find(tree, "tech-iso")
        self.assertIsNotNone(tech_payload)
        # tech subtree holds 3 posts: 1 under ai + 2 under hardware
        self.assertEqual(tech_payload["total_posts"], 3)
        ai_payload = _find(tree, "ai-iso")
        self.assertEqual(ai_payload["total_posts"], 1)

    def test_engagement_aggregator_counts_likes(self):
        agg = category_engagement(self.tech_root.id)
        # the lab 5 ex 2 aggregator stores normalized engagement (0..1 per
        # post, summed). we just need it to be strictly positive on a subtree
        # that contains liked posts and to roll up `total_posts` correctly.
        self.assertEqual(agg["total_posts"], 3)
        self.assertGreater(agg["total_engagement"], 0)


def _find(node, name):
    if node is None:
        return None
    if isinstance(node, dict):
        if node.get("name") == name:
            return node
        for child in node.get("children", []) or []:
            hit = _find(child, name)
            if hit is not None:
                return hit
    return None
