"""
binary max heap for the trending posts feed.

ref: lab 8 exercise 2 (binary_heap_trending_posts_feed). the lab keyed on raw
likes; we key on the composite engagement score from `scoring.py` so the
trending feed stays consistent with the home feed ranking.

claude.md section 5.8 calls out this heap as the way to retrieve top k posts
without sorting the full database. heap operations are O(log n) and top k
is O(k log n) using a transient copy, matching the lab implementation.
"""

from __future__ import annotations

import math
import threading
from typing import Dict, List, Optional, Tuple


class TrendingHeap:
    def __init__(self) -> None:
        # each node: [score, post_id, payload]
        self.heap: List[List] = []
        self.position: Dict[int, int] = {}
        self._lock = threading.RLock()

    @staticmethod
    def parent(i: int) -> int:
        return (i - 1) // 2

    @staticmethod
    def left(i: int) -> int:
        return 2 * i + 1

    @staticmethod
    def right(i: int) -> int:
        return 2 * i + 2

    def _swap(self, i: int, j: int) -> None:
        self.position[self.heap[i][1]] = j
        self.position[self.heap[j][1]] = i
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def _heapify_up(self, i: int) -> None:
        while i > 0:
            p = self.parent(i)
            if self.heap[i][0] > self.heap[p][0]:
                self._swap(i, p)
                i = p
            else:
                break

    def _heapify_down(self, i: int) -> None:
        n = len(self.heap)
        while True:
            largest = i
            l = self.left(i)
            r = self.right(i)
            if l < n and self.heap[l][0] > self.heap[largest][0]:
                largest = l
            if r < n and self.heap[r][0] > self.heap[largest][0]:
                largest = r
            if largest != i:
                self._swap(i, largest)
                i = largest
            else:
                break

    def push(self, post_id: int, score: float, payload: Optional[dict] = None) -> None:
        with self._lock:
            if post_id in self.position:
                self.update(post_id, score, payload)
                return
            node = [score, post_id, payload or {}]
            self.heap.append(node)
            idx = len(self.heap) - 1
            self.position[post_id] = idx
            self._heapify_up(idx)

    def update(self, post_id: int, new_score: float, payload: Optional[dict] = None) -> None:
        with self._lock:
            if post_id not in self.position:
                self.push(post_id, new_score, payload)
                return
            i = self.position[post_id]
            old_score = self.heap[i][0]
            self.heap[i][0] = new_score
            if payload is not None:
                self.heap[i][2] = payload
            if new_score > old_score:
                self._heapify_up(i)
            else:
                self._heapify_down(i)

    def remove(self, post_id: int) -> None:
        with self._lock:
            if post_id not in self.position:
                return
            i = self.position.pop(post_id)
            last = self.heap.pop()
            if i < len(self.heap):
                self.heap[i] = last
                self.position[last[1]] = i
                self._heapify_down(i)
                self._heapify_up(i)

    def pop_max(self) -> Optional[List]:
        with self._lock:
            if not self.heap:
                return None
            top = self.heap[0]
            last = self.heap.pop()
            if self.heap:
                self.heap[0] = last
                self.position[last[1]] = 0
                self._heapify_down(0)
            self.position.pop(top[1], None)
            return top

    def peek_max(self) -> Optional[List]:
        with self._lock:
            return list(self.heap[0]) if self.heap else None

    def get_top_k(self, k: int) -> List[List]:
        """ref: lab 8 ex 2 get_top_k. transient heap copy keeps the original intact."""
        with self._lock:
            temp = TrendingHeap()
            for node in self.heap:
                temp.push(node[1], node[0], node[2])
            out: List[List] = []
            for _ in range(min(k, len(self.heap))):
                popped = temp.pop_max()
                if popped is not None:
                    out.append(popped)
            return out

    def size(self) -> int:
        return len(self.heap)

    def height(self) -> int:
        if not self.heap:
            return 0
        return math.floor(math.log2(len(self.heap)))

    def is_valid(self, i: int = 0) -> bool:
        n = len(self.heap)
        if i >= n:
            return True
        l = self.left(i)
        r = self.right(i)
        if l < n and self.heap[l][0] > self.heap[i][0]:
            return False
        if r < n and self.heap[r][0] > self.heap[i][0]:
            return False
        return self.is_valid(l) and self.is_valid(r)

    def reset(self) -> None:
        with self._lock:
            self.heap.clear()
            self.position.clear()


# process wide singleton, populated by the feed service.
_trending = TrendingHeap()
_lock = threading.Lock()
_hydrated = False


def get_trending_heap() -> TrendingHeap:
    return _trending


def hydrate_trending(items: List[Tuple[int, float, dict]]) -> TrendingHeap:
    """rebuild the singleton heap from precomputed (post_id, score, payload) tuples."""
    global _hydrated
    with _lock:
        _trending.reset()
        for post_id, score, payload in items:
            _trending.push(post_id, score, payload)
        _hydrated = True
    return _trending


def is_hydrated() -> bool:
    return _hydrated


def mark_dirty() -> None:
    """invalidate the singleton so the next call re hydrates."""
    global _hydrated
    with _lock:
        _hydrated = False
