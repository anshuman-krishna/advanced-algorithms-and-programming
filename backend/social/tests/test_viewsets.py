"""
django integration tests for the social viewsets.

ref: phase 6 follow-up. boots an in-memory sqlite, exercises follow,
relationship, suggestion, communities, shortest-chain endpoints end to end.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from social.models import Follow

User = get_user_model()


class SocialViewsetIntegrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.alice = User.objects.create_user(username="alice", password="x")
        cls.bob = User.objects.create_user(username="bob", password="x")
        cls.carol = User.objects.create_user(username="carol", password="x")
        cls.dave = User.objects.create_user(username="dave", password="x")
        # connected: alice -> bob -> carol
        Follow.objects.create(follower=cls.alice, following=cls.bob)
        Follow.objects.create(follower=cls.bob, following=cls.carol)
        # dave is an isolate

    def setUp(self):
        # signals handle cache hydration; force a clean rebuild between tests
        from algorithms.follow_graph import _graph
        _graph.reset()

    def test_relationship_endpoint(self):
        client = APIClient()
        r = client.get("/api/social/relationship/alice/bob/")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertTrue(body["a_follows_b"])
        self.assertFalse(body["b_follows_a"])
        # cache header for the session level shortcut
        self.assertIn("Cache-Control", r.headers)

    def test_communities_groups_isolates_separately(self):
        client = APIClient()
        r = client.get("/api/social/communities/")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        sizes = sorted(c["size"] for c in body["components"])
        # one cluster of 3 (alice/bob/carol) + one isolate (dave)
        self.assertEqual(sizes, [1, 3])

    def test_shortest_chain_finds_path(self):
        client = APIClient()
        r = client.get("/api/social/shortest-chain/?from=alice&to=carol")
        body = r.json()
        usernames = [u["username"] for u in body["chain"]]
        self.assertEqual(usernames, ["alice", "bob", "carol"])
        self.assertEqual(body["length"], 2)

    def test_shortest_chain_disconnected_returns_empty(self):
        client = APIClient()
        r = client.get("/api/social/shortest-chain/?from=alice&to=dave")
        self.assertEqual(r.json()["chain"], [])

    def test_reach_layers(self):
        client = APIClient()
        r = client.get("/api/social/users/alice/reach/")
        body = r.json()
        depths = [layer["depth"] for layer in body["layers"]]
        self.assertEqual(depths, [0, 1, 2])

    def test_followers_endpoint_respects_privacy(self):
        client = APIClient()
        # mark carol private; an anonymous viewer should see private: true
        self.carol.is_private = True
        self.carol.save(update_fields=["is_private"])
        r = client.get("/api/social/users/carol/followers/")
        body = r.json()
        self.assertTrue(body["private"])
        self.assertEqual(body["count"], 0)

        # bob follows carol so they should see the real list
        client.force_authenticate(self.bob)
        r = client.get("/api/social/users/carol/followers/")
        body = r.json()
        # private flag still surfaces but the list is populated
        self.assertTrue(body["private"])
        self.assertGreaterEqual(body["count"], 1)
