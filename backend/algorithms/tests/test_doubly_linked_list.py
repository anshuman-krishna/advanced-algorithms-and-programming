"""
ref: lab 3 ex 1 doubly linked list for content feed navigation.
"""

import unittest

from algorithms.doubly_linked_list import DoublyLinkedList


class DoublyLinkedListTests(unittest.TestCase):
    def setUp(self):
        self.dll = DoublyLinkedList()
        for i in range(1, 6):
            self.dll.append(i, {"caption": f"post {i}"})

    def test_initial_pointers(self):
        self.assertEqual(self.dll.head.key, 1)
        self.assertEqual(self.dll.tail.key, 5)
        self.assertEqual(self.dll.current.key, 1)
        self.assertEqual(self.dll.size, 5)

    def test_keys_in_order(self):
        self.assertEqual(self.dll.keys_in_order(), [1, 2, 3, 4, 5])

    def test_move_forward_and_backward(self):
        self.dll.jump_to(3)
        self.assertEqual(self.dll.move_forward().key, 4)
        self.assertEqual(self.dll.move_forward().key, 5)
        self.assertIsNone(self.dll.move_forward())
        self.assertEqual(self.dll.move_backward().key, 4)

    def test_jump_to_unknown(self):
        self.assertIsNone(self.dll.jump_to(99))
        # cursor unchanged
        self.assertEqual(self.dll.current.key, 1)

    def test_insert_after_wires_neighbors(self):
        self.dll.insert_after(2, 99, {"caption": "breaking"})
        self.assertEqual(self.dll.keys_in_order(), [1, 2, 99, 3, 4, 5])
        # both neighbors must point to the new node
        node = self.dll.jump_to(99)
        self.assertEqual(node.prev.key, 2)
        self.assertEqual(node.next.key, 3)

    def test_insert_after_unknown_anchor_returns_none(self):
        self.assertIsNone(self.dll.insert_after(123, 7))
        self.assertEqual(self.dll.keys_in_order(), [1, 2, 3, 4, 5])

    def test_insert_after_dedup_existing_key(self):
        self.assertIsNone(self.dll.insert_after(1, 3))

    def test_remove_relinks(self):
        self.assertTrue(self.dll.remove(3))
        self.assertEqual(self.dll.keys_in_order(), [1, 2, 4, 5])
        # neighbors should now point to each other
        node2 = self.dll.jump_to(2)
        self.assertEqual(node2.next.key, 4)
        self.assertEqual(node2.next.prev.key, 2)

    def test_remove_head_advances_head(self):
        self.dll.remove(1)
        self.assertEqual(self.dll.head.key, 2)
        self.assertIsNone(self.dll.head.prev)

    def test_remove_tail_retracts_tail(self):
        self.dll.remove(5)
        self.assertEqual(self.dll.tail.key, 4)
        self.assertIsNone(self.dll.tail.next)

    def test_track_view_and_most_viewed(self):
        self.dll.jump_to(2)
        for _ in range(3):
            self.dll.track_view()
        self.dll.jump_to(4)
        self.dll.track_view()
        best = self.dll.most_viewed()
        self.assertEqual(best.key, 2)
        self.assertEqual(best.views, 3)

    def test_slice_around_cursor(self):
        self.dll.jump_to(3)
        keys = [n.key for n in self.dll.slice_around_cursor(1)]
        self.assertEqual(keys, [2, 3, 4])
        keys = [n.key for n in self.dll.slice_around_cursor(2)]
        self.assertEqual(keys, [1, 2, 3, 4, 5])

    def test_page_forward_with_cursor(self):
        nodes, next_cursor = self.dll.page(anchor_key=2, direction="next", limit=2)
        self.assertEqual([n.key for n in nodes], [3, 4])
        self.assertEqual(next_cursor, 4)

    def test_page_backward_returns_reversed(self):
        nodes, next_cursor = self.dll.page(anchor_key=4, direction="prev", limit=2)
        self.assertEqual([n.key for n in nodes], [3, 2])
        self.assertEqual(next_cursor, 2)

    def test_page_no_anchor_starts_from_head(self):
        nodes, next_cursor = self.dll.page(anchor_key=None, direction="next", limit=3)
        self.assertEqual([n.key for n in nodes], [1, 2, 3])
        self.assertEqual(next_cursor, 3)

    def test_hydrate_replaces_state(self):
        self.dll.hydrate([(7, {}), (8, {})])
        self.assertEqual(self.dll.keys_in_order(), [7, 8])
        self.assertEqual(self.dll.current.key, 7)


if __name__ == "__main__":
    unittest.main()
