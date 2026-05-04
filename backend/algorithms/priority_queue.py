"""
linked list priority queue ordered by engagement score.

ref: lab 3 exercise 3 (engagement_based_priority). the lab inserts each post
into a singly linked list while keeping the head as the highest score, so
display walks the chain in priority order without an explicit sort.

we keep the linked list shape on purpose to mirror the lab; the home feed
calls into this for the personalized timeline path. the trending feed uses
the binary heap in `max_heap.py` instead.
"""

from __future__ import annotations

from typing import Iterator, List, Optional


class FeedNode:
    __slots__ = ("post_id", "score", "payload", "next")

    def __init__(self, post_id: int, score: float, payload: Optional[dict] = None) -> None:
        self.post_id = post_id
        self.score = score
        self.payload = payload or {}
        self.next: Optional["FeedNode"] = None


class FeedPriorityQueue:
    """singly linked, head holds the maximum score."""

    def __init__(self) -> None:
        self.head: Optional[FeedNode] = None
        self._count: int = 0

    def __len__(self) -> int:
        return self._count

    def __iter__(self) -> Iterator[FeedNode]:
        cur = self.head
        while cur is not None:
            yield cur
            cur = cur.next

    def insert(self, post_id: int, score: float, payload: Optional[dict] = None) -> None:
        node = FeedNode(post_id, score, payload)
        # ref: lab 3 ex 3 insert_post. insertion at head when empty or strictly greater.
        if self.head is None or score > self.head.score:
            node.next = self.head
            self.head = node
            self._count += 1
            return
        current = self.head
        while current.next is not None and current.next.score >= score:
            current = current.next
        node.next = current.next
        current.next = node
        self._count += 1

    def peek(self) -> Optional[FeedNode]:
        return self.head

    def pop(self) -> Optional[FeedNode]:
        if self.head is None:
            return None
        node = self.head
        self.head = node.next
        node.next = None
        self._count -= 1
        return node

    def to_list(self) -> List[dict]:
        return [
            {"post_id": n.post_id, "score": n.score, **n.payload}
            for n in self
        ]

    def slice(self, offset: int, limit: int) -> List[dict]:
        """
        return a window of the queue without rebuilding it.

        ref: lab 1 ex 5 (array rotation) emphasis on linear time slicing for
        feed pagination. we walk the chain once to skip `offset` and once
        more to collect `limit` nodes.
        """
        out: List[dict] = []
        cur = self.head
        skipped = 0
        while cur is not None and skipped < offset:
            cur = cur.next
            skipped += 1
        taken = 0
        while cur is not None and taken < limit:
            out.append({"post_id": cur.post_id, "score": cur.score, **cur.payload})
            cur = cur.next
            taken += 1
        return out
