"""ref: lab 8 ex 3 prefix and range trees (segment tree portion)."""

import unittest
from datetime import date, timedelta

from algorithms.segment_tree import DailySegmentTree, SegmentTree


class SegmentTreeSumTests(unittest.TestCase):
    def setUp(self):
        self.tree = SegmentTree(8)
        self.tree.build([1, 2, 3, 4, 5, 6, 7, 8])

    def test_full_range_is_sum(self):
        self.assertEqual(self.tree.range_query(0, 8), 36)
        self.assertEqual(self.tree.total(), 36)

    def test_partial_range_inclusive_lo_exclusive_hi(self):
        # indices 2..5 -> values 3, 4, 5
        self.assertEqual(self.tree.range_query(2, 5), 12)

    def test_empty_range_returns_identity(self):
        self.assertEqual(self.tree.range_query(3, 3), 0)
        self.assertEqual(self.tree.range_query(5, 4), 0)

    def test_point_update_propagates(self):
        self.tree.point_update(0, 10)
        self.assertEqual(self.tree.range_query(0, 1), 11)
        self.assertEqual(self.tree.total(), 46)

    def test_point_set_overwrites(self):
        self.tree.point_set(7, 100)
        self.assertEqual(self.tree.range_query(7, 8), 100)
        self.assertEqual(self.tree.total(), 36 - 8 + 100)

    def test_clamps_out_of_range(self):
        # negative lo and oversized hi should still work
        self.assertEqual(self.tree.range_query(-5, 100), 36)


class SegmentTreeMaxTests(unittest.TestCase):
    def test_max_aggregator_returns_peak(self):
        # neutral element for max is -inf; identity must match
        tree = SegmentTree(5, identity=float("-inf"), combine=max)
        tree.build([3, 1, 4, 1, 5])
        self.assertEqual(tree.range_query(0, 5), 5)
        self.assertEqual(tree.range_query(0, 3), 4)
        tree.point_set(0, 9)
        self.assertEqual(tree.range_query(0, 3), 9)


class SegmentTreeBuildEdgeCases(unittest.TestCase):
    def test_size_one(self):
        tree = SegmentTree(1)
        tree.build([7])
        self.assertEqual(tree.range_query(0, 1), 7)
        tree.point_update(0, 3)
        self.assertEqual(tree.total(), 10)

    def test_non_power_of_two_size(self):
        tree = SegmentTree(7)
        tree.build([1, 2, 3, 4, 5, 6, 7])
        self.assertEqual(tree.total(), 28)
        self.assertEqual(tree.range_query(2, 6), 18)

    def test_build_rejects_oversized_input(self):
        tree = SegmentTree(3)
        with self.assertRaises(ValueError):
            tree.build([1, 2, 3, 4])

    def test_invalid_size_raises(self):
        with self.assertRaises(ValueError):
            SegmentTree(0)


class DailySegmentTreeTests(unittest.TestCase):
    def setUp(self):
        self.origin = date(2026, 1, 1)
        self.dst = DailySegmentTree(self.origin, window_days=30)

    def test_add_and_query_inclusive_range(self):
        self.dst.add(self.origin)
        self.dst.add(self.origin + timedelta(days=2), 5)
        self.dst.add(self.origin + timedelta(days=5), 3)
        # range covers day 0 and day 2 -> 1 + 5
        self.assertEqual(self.dst.query(self.origin, self.origin + timedelta(days=4)), 6)
        # full range -> all three
        self.assertEqual(self.dst.query(self.origin, self.origin + timedelta(days=29)), 9)

    def test_add_outside_window_is_dropped(self):
        ok = self.dst.add(self.origin + timedelta(days=999))
        self.assertFalse(ok)
        self.assertEqual(self.dst.total(), 0)

    def test_set_overwrites(self):
        self.dst.add(self.origin, 4)
        self.dst.set(self.origin, 10)
        self.assertEqual(self.dst.query(self.origin, self.origin), 10)

    def test_query_clamps_negative_start(self):
        self.dst.add(self.origin, 7)
        before = self.origin - timedelta(days=10)
        self.assertEqual(self.dst.query(before, self.origin), 7)

    def test_daily_series_length(self):
        self.assertEqual(len(self.dst.daily_series()), 30)


if __name__ == "__main__":
    unittest.main()
