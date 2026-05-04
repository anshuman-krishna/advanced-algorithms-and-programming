"""
iterative segment tree over a fixed length array.

ref: claude.md section 5.8 (lab 8 segment trees for activity analytics).
ref: lab 8 exercise 3 (prefix and range trees) outline. the lab handout sketched
the api shape (insert, range_sum) but only landed the trie portion. we build
the segment tree from scratch and ship the same shape so the analytics layer
can answer "total likes between date X and date Y" in O(log n) per query.

we keep two operations bundled into one class via a `combine` callable so the
same primitive serves sum aggregation (range_sum) and max aggregation
(range_max for top engagement bucket lookups). this is intentional: the lab
notes called out swapping the aggregator as the way to reuse the structure.

design notes
- iterative bottom up segment tree on a power of two padded array. simpler than
  the recursive variant and friendlier to the python interpreter at large n.
- point_update lets the analytics layer increment a bucket on every Like create
  without rebuilding the tree.
- range_query is half open [lo, hi). the bucket adapter below converts dates to
  indices so callers never deal with raw offsets.
"""

from __future__ import annotations

import threading
from datetime import date, timedelta
from typing import Callable, List, Optional


class SegmentTree:
    """
    generic segment tree with pluggable aggregator.

    ref: lab 8 ex 3 prefix and range trees blueprint.
    """

    def __init__(self, size: int, *, identity: float = 0.0,
                 combine: Optional[Callable[[float, float], float]] = None) -> None:
        if size <= 0:
            raise ValueError("size must be positive")
        self.size = size
        self.identity = identity
        self.combine = combine or (lambda a, b: a + b)
        # smallest power of two >= size
        n = 1
        while n < size:
            n *= 2
        self._n = n
        self._tree: List[float] = [identity] * (2 * n)
        self._lock = threading.RLock()

    def build(self, values: List[float]) -> None:
        """O(n) bulk build. ref: lab 8 ex 3 build hint."""
        if len(values) > self.size:
            raise ValueError("values longer than declared size")
        with self._lock:
            for i, v in enumerate(values):
                self._tree[self._n + i] = v
            # fill the unused tail with identity
            for i in range(len(values), self._n):
                self._tree[self._n + i] = self.identity
            for i in range(self._n - 1, 0, -1):
                self._tree[i] = self.combine(self._tree[2 * i], self._tree[2 * i + 1])

    def point_set(self, index: int, value: float) -> None:
        """overwrite the leaf at `index` and propagate."""
        if not 0 <= index < self.size:
            raise IndexError(index)
        with self._lock:
            i = self._n + index
            self._tree[i] = value
            i //= 2
            while i >= 1:
                self._tree[i] = self.combine(self._tree[2 * i], self._tree[2 * i + 1])
                i //= 2

    def point_update(self, index: int, delta: float) -> None:
        """add `delta` to the leaf at `index` and propagate. assumes additive combine."""
        if not 0 <= index < self.size:
            raise IndexError(index)
        with self._lock:
            i = self._n + index
            self._tree[i] = self.combine(self._tree[i], delta)
            i //= 2
            while i >= 1:
                self._tree[i] = self.combine(self._tree[2 * i], self._tree[2 * i + 1])
                i //= 2

    def range_query(self, lo: int, hi: int) -> float:
        """
        aggregate over the half open interval [lo, hi).

        ref: lab 8 ex 3 range_sum signature; here we return whatever the combine
        function dictates (sum, max, etc.).
        """
        if lo < 0:
            lo = 0
        if hi > self.size:
            hi = self.size
        if lo >= hi:
            return self.identity
        with self._lock:
            res_left = self.identity
            res_right = self.identity
            l = lo + self._n
            r = hi + self._n
            while l < r:
                if l & 1:
                    res_left = self.combine(res_left, self._tree[l])
                    l += 1
                if r & 1:
                    r -= 1
                    res_right = self.combine(self._tree[r], res_right)
                l //= 2
                r //= 2
            return self.combine(res_left, res_right)

    def total(self) -> float:
        return self._tree[1]

    def to_list(self) -> List[float]:
        """leaves in index order. used by tests and debug endpoints."""
        return list(self._tree[self._n:self._n + self.size])


# date bucket adapter -----------------------------------------------------------

class DailySegmentTree:
    """
    segment tree indexed by day offset from a fixed origin.

    ref: lab 8 ex 3 range_sum, applied to per-day engagement buckets.

    callers ask "how many likes did user X get between date A and date B" and
    we translate the dates to index offsets, then defer to the underlying tree.
    if a date falls outside the configured window we silently clamp to the
    [origin, origin + window) range.
    """

    def __init__(self, origin: date, window_days: int = 365) -> None:
        if window_days <= 0:
            raise ValueError("window_days must be positive")
        self.origin = origin
        self.window_days = window_days
        self.tree = SegmentTree(window_days)

    def _index(self, day: date) -> int:
        return (day - self.origin).days

    def add(self, day: date, count: float = 1.0) -> bool:
        idx = self._index(day)
        if not 0 <= idx < self.window_days:
            return False
        self.tree.point_update(idx, count)
        return True

    def set(self, day: date, value: float) -> bool:
        idx = self._index(day)
        if not 0 <= idx < self.window_days:
            return False
        self.tree.point_set(idx, value)
        return True

    def query(self, start: date, end_inclusive: date) -> float:
        """range over [start, end] inclusive on both ends."""
        lo = max(0, self._index(start))
        hi = min(self.window_days, self._index(end_inclusive) + 1)
        return self.tree.range_query(lo, hi)

    def total(self) -> float:
        return self.tree.total()

    def daily_series(self) -> List[float]:
        """return the leaves so the frontend can plot the histogram."""
        return self.tree.to_list()
