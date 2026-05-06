"""
phase 6 follow-up: assert that the geo signals correctly upsert + remove the
underlying lab 7 quadtree as Posts are created and deleted.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Post
from geo import services as geo_services

User = get_user_model()


class GeoSignalIntegrationTests(TestCase):
    def setUp(self):
        geo_services.force_reset()
        self.user = User.objects.create_user(username="cartographer", password="x")

    def test_post_with_coords_lands_in_quadtree(self):
        before = geo_services.stats()["size"]
        Post.objects.create(
            author=self.user,
            caption="lisbon",
            latitude=38.72, longitude=-9.14,
        )
        after = geo_services.stats()["size"]
        self.assertEqual(after, before + 1)

    def test_post_without_coords_skipped(self):
        before = geo_services.stats()["size"]
        Post.objects.create(author=self.user, caption="no coords")
        after = geo_services.stats()["size"]
        self.assertEqual(after, before)

    def test_post_delete_removes_from_quadtree(self):
        post = Post.objects.create(
            author=self.user,
            caption="tokyo",
            latitude=35.68, longitude=139.65,
        )
        size_with = geo_services.stats()["size"]
        post.delete()
        size_without = geo_services.stats()["size"]
        self.assertLess(size_without, size_with)

    def test_nearby_returns_recent_post(self):
        Post.objects.create(
            author=self.user,
            caption="nyc",
            latitude=40.71, longitude=-74.0,
        )
        results = geo_services.nearby(40.71, -74.0, radius_deg=0.5)
        self.assertTrue(any(r.get("caption") == "nyc" for r in results))
