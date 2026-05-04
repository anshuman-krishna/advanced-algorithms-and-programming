"""
ref: lab 8 ex 2 trending heap.
"""

import unittest

from algorithms.max_heap import TrendingHeap


class TrendingHeapTests(unittest.TestCase):
    def setUp(self):
        self.h = TrendingHeap()
        self.h.push(1, 0.5)
        self.h.push(2, 0.9)
        self.h.push(3, 0.3)
        self.h.push(4, 0.7)

    def test_peek_max_is_highest_score(self):
        self.assertEqual(self.h.peek_max()[1], 2)

    def test_pop_max_returns_descending(self):
        order = []
        while self.h.size() > 0:
            order.append(self.h.pop_max()[1])
        self.assertEqual(order, [2, 4, 1, 3])

    def test_top_k_does_not_mutate(self):
        top = self.h.get_top_k(2)
        self.assertEqual([n[1] for n in top], [2, 4])
        self.assertEqual(self.h.size(), 4)

    def test_update_promotes_node(self):
        self.h.update(3, 1.0)
        self.assertEqual(self.h.peek_max()[1], 3)

    def test_update_unknown_post_inserts(self):
        self.h.update(99, 0.42)
        self.assertEqual(self.h.size(), 5)

    def test_remove_arbitrary_node(self):
        self.h.remove(2)
        self.assertEqual(self.h.size(), 3)
        self.assertEqual(self.h.peek_max()[1], 4)

    def test_is_valid_after_random_ops(self):
        self.h.push(5, 0.95)
        self.h.update(1, 0.4)
        self.h.pop_max()
        self.h.push(6, 0.1)
        self.assertTrue(self.h.is_valid())

    def test_payload_round_trip(self):
        self.h.push(10, 0.42, {"caption": "hi"})
        node = next(n for n in self.h.heap if n[1] == 10)
        self.assertEqual(node[2]["caption"], "hi")


if __name__ == "__main__":
    unittest.main()
