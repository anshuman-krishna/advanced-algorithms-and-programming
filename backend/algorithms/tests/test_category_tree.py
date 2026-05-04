"""
ref: lab 5 ex 3 generalized trees, lab 5 ex 2 post order aggregation.
"""

import unittest

from algorithms.category_tree import (
    CategoryNode,
    build_from_rows,
    collect_subtree_post_ids,
    count_nodes,
    find,
    height,
    level_order,
    post_order_aggregate,
    pre_order_names,
    serialize,
)


class CategoryTreeTests(unittest.TestCase):
    def setUp(self):
        rows = [
            {"id": 1, "name": "explore", "parent_id": None},
            {"id": 2, "name": "tech", "parent_id": 1},
            {"id": 3, "name": "ai", "parent_id": 2},
            {"id": 4, "name": "hardware", "parent_id": 2},
            {"id": 5, "name": "fashion", "parent_id": 1},
            {"id": 6, "name": "streetwear", "parent_id": 5},
        ]
        self.root = build_from_rows(rows)
        self.root.children[0].children[0].post_ids = {100, 101}
        self.root.children[0].children[1].post_ids = {200}
        self.root.children[1].children[0].post_ids = {300, 301, 302}

    def test_pre_order_names(self):
        self.assertEqual(
            pre_order_names(self.root),
            ["explore", "tech", "ai", "hardware", "fashion", "streetwear"],
        )

    def test_level_order(self):
        self.assertEqual(
            level_order(self.root),
            ["explore", "tech", "fashion", "ai", "hardware", "streetwear"],
        )

    def test_height(self):
        self.assertEqual(height(self.root), 3)

    def test_count_nodes(self):
        self.assertEqual(count_nodes(self.root), 6)

    def test_find(self):
        node = find(self.root, 4)
        self.assertIsNotNone(node)
        self.assertEqual(node.name, "hardware")

    def test_collect_subtree_post_ids(self):
        tech = find(self.root, 2)
        self.assertEqual(collect_subtree_post_ids(tech), {100, 101, 200})

    def test_post_order_aggregate_engagement(self):
        engagement = {100: 1.0, 101: 2.0, 200: 4.0, 300: 0.5, 301: 0.5, 302: 0.5}
        post_order_aggregate(self.root, engagement)
        explore = self.root
        tech = find(self.root, 2)
        fashion = find(self.root, 5)
        self.assertAlmostEqual(tech.total_engagement, 7.0)
        self.assertAlmostEqual(fashion.total_engagement, 1.5)
        self.assertAlmostEqual(explore.total_engagement, 8.5)
        self.assertEqual(tech.total_posts, 3)
        self.assertEqual(explore.total_posts, 6)

    def test_serialize_round_trip(self):
        post_order_aggregate(self.root, {})
        payload = serialize(self.root)
        self.assertEqual(payload["name"], "explore")
        self.assertEqual(len(payload["children"]), 2)

    def test_synthetic_root_for_forest(self):
        rows = [
            {"id": 1, "name": "a", "parent_id": None},
            {"id": 2, "name": "b", "parent_id": None},
        ]
        root = build_from_rows(rows)
        self.assertEqual(root.name, "explore")
        self.assertEqual(len(root.children), 2)


if __name__ == "__main__":
    unittest.main()
