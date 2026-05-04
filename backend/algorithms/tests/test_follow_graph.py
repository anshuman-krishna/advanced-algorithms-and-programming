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


class FollowGraphTraversalTests(unittest.TestCase):
    """ref: lab 6 ex 2 dfs connected components, lab 6 ex 3 bfs shortest path."""

    def setUp(self):
        # build two disjoint clusters: {1,2,3,4} and {10,11,12}, plus an isolate 99
        self.g = FollowGraph()
        for uid in [1, 2, 3, 4, 10, 11, 12, 99]:
            self.g.add_user(uid)
        # cluster a (chain 1->2->3->4)
        for follower, target in [(1, 2), (2, 3), (3, 4)]:
            self.g.add_edge(follower, target)
        # cluster b (triangle 10-11-12)
        for follower, target in [(10, 11), (11, 12), (12, 10)]:
            self.g.add_edge(follower, target)

    def test_connected_components_groups_clusters(self):
        components = self.g.connected_components()
        sizes = sorted(len(c) for c in components)
        self.assertEqual(sizes, [1, 3, 4])
        # largest first per the sort
        self.assertEqual(len(components[0]), 4)
        self.assertEqual(set(components[0]), {1, 2, 3, 4})

    def test_component_of_returns_membership(self):
        members = set(self.g.component_of(2))
        self.assertEqual(members, {1, 2, 3, 4})
        self.assertEqual(self.g.component_of(99), [99])
        self.assertEqual(self.g.component_of(404), [])

    def test_shortest_chain_basic(self):
        chain = self.g.shortest_chain(1, 4)
        self.assertEqual(chain, [1, 2, 3, 4])

    def test_shortest_chain_self_returns_singleton(self):
        self.assertEqual(self.g.shortest_chain(1, 1), [1])

    def test_shortest_chain_disconnected_returns_empty(self):
        self.assertEqual(self.g.shortest_chain(1, 12), [])

    def test_shortest_chain_unknown_node_returns_empty(self):
        self.assertEqual(self.g.shortest_chain(1, 404), [])

    def test_bfs_distances_max_depth(self):
        d = self.g.bfs_distances(1, max_depth=2)
        # at depth 2 we reach node 3 but not 4
        self.assertIn(3, d)
        self.assertNotIn(4, d)
        self.assertEqual(d[1], 0)

    def test_bfs_distances_full(self):
        d = self.g.bfs_distances(1)
        self.assertEqual(d, {1: 0, 2: 1, 3: 2, 4: 3})


if __name__ == "__main__":
    unittest.main()
