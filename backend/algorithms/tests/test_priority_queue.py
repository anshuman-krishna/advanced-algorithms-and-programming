"""
ref: lab 3 ex 3 engagement priority queue.
"""

import unittest

from algorithms.priority_queue import FeedPriorityQueue


class PriorityQueueTests(unittest.TestCase):
    def setUp(self):
        self.pq = FeedPriorityQueue()
        self.pq.insert(1, 0.4)
        self.pq.insert(2, 0.9)
        self.pq.insert(3, 0.6)
        self.pq.insert(4, 0.7)

    def test_head_is_max(self):
        self.assertEqual(self.pq.peek().post_id, 2)

    def test_iteration_is_descending(self):
        self.assertEqual([n.post_id for n in self.pq], [2, 4, 3, 1])

    def test_pop_returns_descending(self):
        out = []
        while len(self.pq):
            out.append(self.pq.pop().post_id)
        self.assertEqual(out, [2, 4, 3, 1])
        self.assertIsNone(self.pq.pop())

    def test_slice_offset_limit(self):
        page = self.pq.slice(offset=1, limit=2)
        self.assertEqual([entry["post_id"] for entry in page], [4, 3])

    def test_slice_past_end(self):
        page = self.pq.slice(offset=10, limit=5)
        self.assertEqual(page, [])

    def test_payload_round_trip(self):
        self.pq.insert(99, 0.99, payload={"caption": "top"})
        head = self.pq.peek()
        self.assertEqual(head.post_id, 99)
        self.assertEqual(head.payload["caption"], "top")

    def test_to_list_includes_payload(self):
        self.pq.insert(7, 0.05, payload={"author": "x"})
        listing = self.pq.to_list()
        last = listing[-1]
        self.assertEqual(last["post_id"], 7)
        self.assertEqual(last["author"], "x")


if __name__ == "__main__":
    unittest.main()
