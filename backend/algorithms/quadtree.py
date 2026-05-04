"""
quadtree for spatial queries on geo tagged posts.

ref: claude.md section 5.7 (lab 7 spatial algorithms).
ref: lab 7 exercise 1 (divide and conquer spatial splitting). the lab built a
top-down recursive splitter that found dense regions; we generalize that into a
proper quadtree node so we can answer two distinct queries:
  1. range_query(rect) for "posts inside this bbox"
  2. nearest(point, k) for "k closest posts to (lat, lng)"

we keep an arbitrary payload per point so the geo service can stash post id,
caption, author, etc. without a follow-up sql query per result.

design notes
- bucket capacity: a node holds up to BUCKET_SIZE points before subdividing.
  small buckets pay too much pointer overhead; large ones make range queries
  scan more leaves. 4 strikes a decent balance for our scale.
- max depth: if all points coincide we would recurse forever, so we cap depth
  at MAX_DEPTH and let a deep leaf hold an unbounded list.
- coordinate convention: x = longitude, y = latitude. callers must use the same.
"""

from __future__ import annotations

import math
import threading
from typing import Any, Iterable, List, Optional, Tuple


BUCKET_SIZE = 4
MAX_DEPTH = 16


class BoundingBox:
    __slots__ = ("min_x", "min_y", "max_x", "max_y")

    def __init__(self, min_x: float, min_y: float, max_x: float, max_y: float) -> None:
        if min_x > max_x or min_y > max_y:
            raise ValueError("bbox is inverted")
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y

    def contains(self, x: float, y: float) -> bool:
        return self.min_x <= x <= self.max_x and self.min_y <= y <= self.max_y

    def intersects(self, other: "BoundingBox") -> bool:
        return not (
            other.min_x > self.max_x
            or other.max_x < self.min_x
            or other.min_y > self.max_y
            or other.max_y < self.min_y
        )

    def quadrants(self) -> Tuple["BoundingBox", "BoundingBox", "BoundingBox", "BoundingBox"]:
        mid_x = (self.min_x + self.max_x) / 2.0
        mid_y = (self.min_y + self.max_y) / 2.0
        # north west, north east, south west, south east. we use latitude up.
        return (
            BoundingBox(self.min_x, mid_y, mid_x, self.max_y),
            BoundingBox(mid_x, mid_y, self.max_x, self.max_y),
            BoundingBox(self.min_x, self.min_y, mid_x, mid_y),
            BoundingBox(mid_x, self.min_y, self.max_x, mid_y),
        )

    def __repr__(self) -> str:
        return f"BoundingBox({self.min_x}, {self.min_y}, {self.max_x}, {self.max_y})"


class _Point:
    __slots__ = ("x", "y", "key", "payload")

    def __init__(self, x: float, y: float, key: Any, payload: Optional[dict]) -> None:
        self.x = x
        self.y = y
        self.key = key
        self.payload = payload or {}


class QuadTree:
    """
    point quadtree with overlap aware insertion and bbox / nearest queries.

    ref: lab 7 ex 1 find_dense_regions for the recursive subdivision shape;
    the lab counted points per region, we store and query them.
    """

    def __init__(self, bbox: BoundingBox, *, depth: int = 0,
                 capacity: int = BUCKET_SIZE) -> None:
        self.bbox = bbox
        self.depth = depth
        self.capacity = capacity
        self.points: List[_Point] = []
        self.children: Optional[Tuple["QuadTree", "QuadTree", "QuadTree", "QuadTree"]] = None
        self._size = 0
        self._lock = threading.RLock()

    @property
    def size(self) -> int:
        return self._size

    def insert(self, x: float, y: float, key: Any,
               payload: Optional[dict] = None) -> bool:
        """ref: lab 7 ex 1 insertion phase. returns False if the point is outside the root bbox."""
        if not self.bbox.contains(x, y):
            return False
        with self._lock:
            self._size += 1
            self._insert(_Point(x, y, key, payload))
            return True

    def _insert(self, point: _Point) -> None:
        if self.children is None:
            if len(self.points) < self.capacity or self.depth >= MAX_DEPTH:
                self.points.append(point)
                return
            self._subdivide()
        for child in self.children:
            if child.bbox.contains(point.x, point.y):
                child._insert(point)
                child._size += 1
                return
        # fallback in case of float boundary weirdness
        self.points.append(point)

    def _subdivide(self) -> None:
        nw, ne, sw, se = self.bbox.quadrants()
        self.children = (
            QuadTree(nw, depth=self.depth + 1, capacity=self.capacity),
            QuadTree(ne, depth=self.depth + 1, capacity=self.capacity),
            QuadTree(sw, depth=self.depth + 1, capacity=self.capacity),
            QuadTree(se, depth=self.depth + 1, capacity=self.capacity),
        )
        # redistribute existing points into children
        existing = self.points
        self.points = []
        for pt in existing:
            placed = False
            for child in self.children:
                if child.bbox.contains(pt.x, pt.y):
                    child._insert(pt)
                    child._size += 1
                    placed = True
                    break
            if not placed:
                self.points.append(pt)

    def remove(self, key: Any) -> bool:
        """linear scan within the relevant subtrees; quad index lookup is O(log n) average."""
        with self._lock:
            removed = self._remove(key)
            if removed:
                self._size -= 1
            return removed

    def _remove(self, key: Any) -> bool:
        for i, pt in enumerate(self.points):
            if pt.key == key:
                self.points.pop(i)
                return True
        if self.children is not None:
            for child in self.children:
                if child._remove(key):
                    child._size -= 1
                    return True
        return False

    # range queries ------------------------------------------------------------
    def range_query(self, rect: BoundingBox) -> List[dict]:
        """ref: lab 7 ex 1 count_points_in_region but returning the points."""
        out: List[dict] = []
        self._range_query(rect, out)
        return out

    def _range_query(self, rect: BoundingBox, out: List[dict]) -> None:
        if not self.bbox.intersects(rect):
            return
        for pt in self.points:
            if rect.contains(pt.x, pt.y):
                out.append({"key": pt.key, "x": pt.x, "y": pt.y, **pt.payload})
        if self.children is not None:
            for child in self.children:
                child._range_query(rect, out)

    def radius_query(self, x: float, y: float, radius: float) -> List[dict]:
        """
        all points within `radius` (planar distance, not haversine) of (x, y).

        for our scale we treat lat/lng as a flat plane. that under-estimates
        distance near the poles but is fine for the small demo dataset.
        """
        rect = BoundingBox(x - radius, y - radius, x + radius, y + radius)
        candidates = self.range_query(rect)
        r2 = radius * radius
        return [p for p in candidates
                if (p["x"] - x) ** 2 + (p["y"] - y) ** 2 <= r2]

    def nearest(self, x: float, y: float, k: int = 1) -> List[dict]:
        """
        k nearest points by planar distance.

        ref: lab 7 ex 1 recursive subdivision, traversed so the closest quadrant
        is visited first. we keep a bounded heap of the best k seen so far.
        """
        if k <= 0:
            return []
        import heapq

        # we use a max heap by negative distance so we can pop the worst easily
        heap: List[Tuple[float, int, _Point]] = []
        counter = 0

        def visit(node: "QuadTree") -> None:
            nonlocal counter
            for pt in node.points:
                d = (pt.x - x) ** 2 + (pt.y - y) ** 2
                counter += 1
                if len(heap) < k:
                    heapq.heappush(heap, (-d, counter, pt))
                elif -heap[0][0] > d:
                    heapq.heapreplace(heap, (-d, counter, pt))
            if node.children is None:
                return
            # visit child whose bbox is closest to (x, y) first
            ranked = sorted(
                node.children,
                key=lambda c: _bbox_distance_squared(c.bbox, x, y),
            )
            for child in ranked:
                if len(heap) >= k and _bbox_distance_squared(child.bbox, x, y) > -heap[0][0]:
                    continue
                visit(child)

        visit(self)
        out = sorted(((-d, pt) for d, _, pt in heap), key=lambda t: t[0])
        return [
            {"key": pt.key, "x": pt.x, "y": pt.y,
             "distance": math.sqrt(d), **pt.payload}
            for d, pt in out
        ]

    # bulk hydrate -------------------------------------------------------------
    def hydrate(self, items: Iterable[Tuple[float, float, Any, Optional[dict]]]) -> None:
        """rebuild from a flat iterable of (x, y, key, payload)."""
        with self._lock:
            self.points = []
            self.children = None
            self._size = 0
            for x, y, key, payload in items:
                self.insert(x, y, key, payload)

    def all_points(self) -> List[dict]:
        out: List[dict] = []
        for pt in self.points:
            out.append({"key": pt.key, "x": pt.x, "y": pt.y, **pt.payload})
        if self.children is not None:
            for child in self.children:
                out.extend(child.all_points())
        return out


def _bbox_distance_squared(box: BoundingBox, x: float, y: float) -> float:
    """min squared distance from a point to a bbox; 0 if inside."""
    dx = 0.0
    if x < box.min_x:
        dx = box.min_x - x
    elif x > box.max_x:
        dx = x - box.max_x
    dy = 0.0
    if y < box.min_y:
        dy = box.min_y - y
    elif y > box.max_y:
        dy = y - box.max_y
    return dx * dx + dy * dy
