"""
unit tests for the adjacency list helper. runnable without django.

usage: python -m unittest backend.algorithms.tests.test_follow_graph
"""

import unittest

from algorithms.follow_graph import FollowGraph


class FollowGraphTests(unittest.TestCase):
    def setUp(self):
        self.g = FollowGraph()
        for uid in [1, 2, 3, 4]:
            self.g.add_user(uid)

    def test_directed_edge(self):
        self.assertTrue(self.g.add_edge(1, 2))
        self.assertTrue(self.g.is_following(1, 2))
        self.assertFalse(self.g.is_following(2, 1))

    def test_idempotent_add(self):
        self.g.add_edge(1, 2)
        self.assertFalse(self.g.add_edge(1, 2))
        self.assertEqual(self.g.num_edges, 1)

    def test_no_self_loop(self):
        self.assertFalse(self.g.add_edge(1, 1))
        self.assertEqual(self.g.num_edges, 0)

    def test_remove_edge(self):
        self.g.add_edge(1, 2)
        self.assertTrue(self.g.remove_edge(1, 2))
        self.assertFalse(self.g.is_following(1, 2))
        self.assertEqual(self.g.num_edges, 0)

    def test_remove_user_clears_edges(self):
        self.g.add_edge(1, 2)
        self.g.add_edge(3, 1)
        self.g.remove_user(1)
        self.assertNotIn(1, self.g.following)
        self.assertNotIn(1, self.g.followers)
        self.assertEqual(self.g.num_edges, 0)

    def test_followers_following_lists(self):
        self.g.add_edge(1, 2)
        self.g.add_edge(3, 2)
        self.assertEqual(self.g.get_followers(2), [1, 3])
        self.assertEqual(self.g.get_following(1), [2])

    def test_density_empty(self):
        empty = FollowGraph()
        self.assertEqual(empty.graph_density(), 0.0)

    def test_density_filled(self):
        # 4 users, 2 directed edges, density = 2 / (4*3) = 0.1666...
        self.g.add_edge(1, 2)
        self.g.add_edge(2, 3)
        self.assertAlmostEqual(self.g.graph_density(), 2 / 12)

    def test_hydrate_replaces_state(self):
        self.g.add_edge(1, 2)
        self.g.hydrate([10, 20, 30], [(10, 20), (20, 30)])
        self.assertEqual(self.g.num_edges, 2)
        self.assertEqual(self.g.get_followers(20), [10])
        self.assertNotIn(1, self.g.following)


if __name__ == "__main__":
    unittest.main()
