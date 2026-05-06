"""ref: lab 7 ex 1 divide and conquer spatial splitting."""

import unittest

from algorithms.quadtree import BoundingBox, QuadTree


def _make() -> QuadTree:
    qt = QuadTree(BoundingBox(0, 0, 100, 100))
    qt.insert(10, 10, "a")
    qt.insert(12, 15, "b")
    qt.insert(80, 80, "c")
    qt.insert(85, 85, "d")
    qt.insert(50, 50, "e")
    return qt


class BoundingBoxTests(unittest.TestCase):
    def test_inverted_bbox_raises(self):
        with self.assertRaises(ValueError):
            BoundingBox(10, 10, 5, 5)

    def test_intersects_disjoint_returns_false(self):
        a = BoundingBox(0, 0, 10, 10)
        b = BoundingBox(20, 20, 30, 30)
        self.assertFalse(a.intersects(b))

    def test_quadrants_partition(self):
        b = BoundingBox(0, 0, 10, 10)
        nw, ne, sw, se = b.quadrants()
        self.assertEqual((nw.min_x, nw.max_y), (0, 10))
        self.assertEqual((ne.max_x, ne.max_y), (10, 10))
        self.assertEqual((sw.min_x, sw.min_y), (0, 0))
        self.assertEqual((se.max_x, se.min_y), (10, 0))


class QuadTreeInsertTests(unittest.TestCase):
    def test_insert_outside_bbox_returns_false(self):
        qt = QuadTree(BoundingBox(0, 0, 10, 10))
        self.assertFalse(qt.insert(20, 20, "x"))
        self.assertEqual(qt.size, 0)

    def test_size_after_inserts(self):
        qt = _make()
        self.assertEqual(qt.size, 5)

    def test_subdivision_after_capacity(self):
        qt = QuadTree(BoundingBox(0, 0, 100, 100), capacity=2)
        for i, (x, y) in enumerate([(10, 10), (12, 12), (80, 80), (90, 10), (10, 90)]):
            qt.insert(x, y, f"p{i}")
        self.assertIsNotNone(qt.children)
        self.assertEqual(qt.size, 5)

    def test_remove_drops_point(self):
        qt = _make()
        self.assertTrue(qt.remove("c"))
        self.assertFalse(qt.remove("missing"))
        self.assertEqual(qt.size, 4)

    def test_hydrate_replaces_state(self):
        qt = _make()
        qt.hydrate([(1, 1, "x", None), (2, 2, "y", {"caption": "hi"})])
        self.assertEqual(qt.size, 2)
        keys = [p["key"] for p in qt.all_points()]
        self.assertEqual(sorted(keys), ["x", "y"])


class QuadTreeRangeTests(unittest.TestCase):
    def test_range_inside_corner(self):
        qt = _make()
        hits = qt.range_query(BoundingBox(0, 0, 20, 20))
        self.assertEqual(sorted(p["key"] for p in hits), ["a", "b"])

    def test_range_full_returns_all(self):
        qt = _make()
        hits = qt.range_query(BoundingBox(0, 0, 100, 100))
        self.assertEqual(len(hits), 5)

    def test_range_disjoint_returns_empty(self):
        qt = _make()
        hits = qt.range_query(BoundingBox(200, 200, 300, 300))
        self.assertEqual(hits, [])

    def test_radius_query_filters_corners(self):
        qt = _make()
        # circle around 10, 10 of radius 5 picks a only
        hits = qt.radius_query(10, 10, 5)
        keys = sorted(p["key"] for p in hits)
        self.assertEqual(keys, ["a"])


class QuadTreeNearestTests(unittest.TestCase):
    def test_nearest_returns_closest(self):
        qt = _make()
        result = qt.nearest(11, 11, k=1)
        self.assertEqual(result[0]["key"], "a")

    def test_nearest_k_returns_sorted(self):
        qt = _make()
        result = qt.nearest(50, 50, k=3)
        keys = [p["key"] for p in result]
        self.assertEqual(keys[0], "e")
        self.assertEqual(len(result), 3)
        # distances must be monotonically non-decreasing
        distances = [p["distance"] for p in result]
        self.assertEqual(distances, sorted(distances))

    def test_nearest_with_k_zero_returns_empty(self):
        qt = _make()
        self.assertEqual(qt.nearest(0, 0, k=0), [])


class QuadTreeDenseRegionsTests(unittest.TestCase):
    """ref: lab 7 ex 1 find_dense_regions."""

    def test_dense_regions_find_clusters(self):
        qt = QuadTree(BoundingBox(0, 0, 100, 100), capacity=2)
        # cluster of points in the bottom-left corner
        for x, y in [(5, 5), (6, 4), (4, 6), (7, 7)]:
            qt.insert(x, y, f"a{x}{y}")
        # one isolated point in the opposite corner
        qt.insert(95, 95, "lone")
        regions = qt.dense_regions(threshold=2, min_size=10)
        # at least one region must include the bottom-left cluster
        in_cluster = [r for r in regions if r["min_x"] < 50 and r["min_y"] < 50 and r["count"] >= 3]
        self.assertTrue(in_cluster)

    def test_dense_regions_respects_min_size(self):
        qt = QuadTree(BoundingBox(0, 0, 100, 100), capacity=2)
        for i in range(8):
            qt.insert(50 + i * 0.1, 50, f"p{i}")
        regions = qt.dense_regions(threshold=1, min_size=200)
        # min_size larger than the bbox side: only the root counts (none if bbox <200)
        self.assertEqual(regions, [])


class QuadTreePathologyTests(unittest.TestCase):
    def test_many_coincident_points_terminate(self):
        qt = QuadTree(BoundingBox(0, 0, 100, 100), capacity=2)
        # 20 points at the same coordinate. capacity should be respected up to
        # MAX_DEPTH and then the leaf should fall back to a flat list.
        for i in range(20):
            self.assertTrue(qt.insert(50, 50, f"p{i}"))
        self.assertEqual(qt.size, 20)
        self.assertEqual(len(qt.range_query(BoundingBox(49, 49, 51, 51))), 20)


if __name__ == "__main__":
    unittest.main()
