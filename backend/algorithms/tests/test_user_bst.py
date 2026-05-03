"""
ref: lab 8 ex 1 verifications.
"""

import unittest

from algorithms.user_bst import UserIndex, inorder, suggest_friends


class UserBSTTests(unittest.TestCase):
    def setUp(self):
        self.index = UserIndex()
        self.index.hydrate(
            [(50, "alice"), (30, "bob"), (70, "carol"), (20, "dave"),
             (40, "eve"), (60, "frank"), (80, "grace")],
            {
                50: {30, 70, 20},
                30: {50, 20, 40},
                70: {50, 60, 80},
                20: {30, 50},
                40: {30, 60},
                60: {70, 40},
                80: {70},
            },
        )

    def test_inorder_returns_sorted_ids(self):
        self.assertEqual(inorder(self.index.root), [20, 30, 40, 50, 60, 70, 80])

    def test_get_returns_node(self):
        node = self.index.get(40)
        self.assertIsNotNone(node)
        self.assertEqual(node.username, "eve")
        self.assertEqual(node.friends, {30, 60})

    def test_suggest_ranks_by_mutual_count(self):
        suggestions = suggest_friends(self.index.root, 20, max_suggestions=3)
        # dave (id 20) follows 30 and 50. friends of friends excluding direct + self
        # 30 -> {40} new, 50 -> {70} new. counts equal so order is stable by dict.
        ids = [uid for uid, _ in suggestions]
        self.assertIn(40, ids)
        self.assertIn(70, ids)

    def test_remove_user_drops_node(self):
        self.index.remove_user(30)
        self.assertIsNone(self.index.get(30))
        self.assertEqual(inorder(self.index.root), [20, 40, 50, 60, 70, 80])

    def test_add_remove_friend(self):
        self.index.add_friend(20, 99)
        self.assertIn(99, self.index.get(20).friends)
        self.index.remove_friend(20, 99)
        self.assertNotIn(99, self.index.get(20).friends)

    def test_stats_shape(self):
        s = self.index.stats()
        self.assertEqual(s["size"], 7)
        self.assertGreaterEqual(s["height"], 3)
        self.assertIn("is_balanced", s)


if __name__ == "__main__":
    unittest.main()
