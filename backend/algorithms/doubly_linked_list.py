"""
doubly linked list driving the reels and stories feed cursor.

ref: claude.md section 5.3 (lab 3 doubly linked lists for swiping mechanism).
ref: lab 3 exercise 1 (content_feed_navigation_with_doubly_linked_list) for the
StoryNode shape, head/tail/current pointers, move_forward, move_backward,
jump_to, insert_after, track_view, most_viewed, display_around_current.

we generalize the lab class so the same dll can drive both reels (posts) and
stories (short lived media). a node carries an arbitrary payload dict so the
api layer can attach the post id, image url, author, etc. without rewriting
the algorithm.
"""

from __future__ import annotations

import threading
from typing import Any, Dict, Iterable, List, Optional, Tuple


class DLLNode:
    __slots__ = ("key", "payload", "views", "prev", "next")

    def __init__(self, key: Any, payload: Optional[dict] = None) -> None:
        self.key = key
        self.payload: dict = payload or {}
        self.views: int = 0
        self.prev: Optional["DLLNode"] = None
        self.next: Optional["DLLNode"] = None


class DoublyLinkedList:
    def __init__(self) -> None:
        self.head: Optional[DLLNode] = None
        self.tail: Optional[DLLNode] = None
        self.current: Optional[DLLNode] = None
        self._index: Dict[Any, DLLNode] = {}
        self._lock = threading.RLock()

    @property
    def size(self) -> int:
        return len(self._index)

    # mutators -----------------------------------------------------------------
    def append(self, key: Any, payload: Optional[dict] = None) -> DLLNode:
        """ref: lab 3 ex 1 add_story. push to tail, set current on first insert."""
        with self._lock:
            if key in self._index:
                # idempotent re insert refreshes payload
                node = self._index[key]
                if payload is not None:
                    node.payload = payload
                return node
            node = DLLNode(key, payload)
            if self.head is None:
                self.head = node
                self.tail = node
                self.current = node
            else:
                node.prev = self.tail
                self.tail.next = node
                self.tail = node
            self._index[key] = node
            return node

    def insert_after(self, anchor_key: Any, key: Any,
                     payload: Optional[dict] = None) -> Optional[DLLNode]:
        """ref: lab 3 ex 1 insert_after. wires the new node between anchor and its successor."""
        with self._lock:
            anchor = self._index.get(anchor_key)
            if anchor is None or key in self._index:
                return None
            node = DLLNode(key, payload)
            node.prev = anchor
            node.next = anchor.next
            if anchor.next is not None:
                anchor.next.prev = node
            else:
                self.tail = node
            anchor.next = node
            self._index[key] = node
            return node

    def remove(self, key: Any) -> bool:
        """ref: lab 3 ex 1 remove_story."""
        with self._lock:
            node = self._index.pop(key, None)
            if node is None:
                return False
            if node.prev is not None:
                node.prev.next = node.next
            else:
                self.head = node.next
            if node.next is not None:
                node.next.prev = node.prev
            else:
                self.tail = node.prev
            if self.current is node:
                self.current = node.next or node.prev
            return True

    # navigation ---------------------------------------------------------------
    def jump_to(self, key: Any) -> Optional[DLLNode]:
        """ref: lab 3 ex 1 jump_to. set the cursor by key, O(1) via the index."""
        with self._lock:
            node = self._index.get(key)
            if node is not None:
                self.current = node
            return node

    def move_forward(self) -> Optional[DLLNode]:
        """ref: lab 3 ex 1 move_forward. returns None at end of feed."""
        with self._lock:
            if self.current is None or self.current.next is None:
                return None
            self.current = self.current.next
            return self.current

    def move_backward(self) -> Optional[DLLNode]:
        """ref: lab 3 ex 1 move_backward. returns None at beginning of feed."""
        with self._lock:
            if self.current is None or self.current.prev is None:
                return None
            self.current = self.current.prev
            return self.current

    # views and ranking --------------------------------------------------------
    def track_view(self) -> Optional[DLLNode]:
        """ref: lab 3 ex 1 track_view. increments the view counter on the cursor."""
        with self._lock:
            if self.current is not None:
                self.current.views += 1
            return self.current

    def most_viewed(self) -> Optional[DLLNode]:
        """ref: lab 3 ex 1 most_viewed. linear scan, returns the highest views node."""
        with self._lock:
            best: Optional[DLLNode] = None
            for node in self._index.values():
                if best is None or node.views > best.views:
                    best = node
            return best

    # window slicing -----------------------------------------------------------
    def slice_around_cursor(self, k: int) -> List[DLLNode]:
        """
        return up to (2k + 1) nodes centered on the cursor, prev k then current
        then next k. ref: lab 3 ex 1 display_around_current.
        """
        with self._lock:
            if self.current is None:
                return []
            # walk back at most k steps
            start = self.current
            for _ in range(k):
                if start.prev is None:
                    break
                start = start.prev
            out: List[DLLNode] = []
            limit = (2 * k) + 1
            cursor = start
            while cursor is not None and len(out) < limit:
                out.append(cursor)
                cursor = cursor.next
            return out

    def page(self, anchor_key: Optional[Any], direction: str = "next",
             limit: int = 5) -> Tuple[List[DLLNode], Optional[Any]]:
        """
        cursor pagination: starting from anchor_key (exclusive), walk in the
        given direction up to `limit` nodes. returns (nodes, next_cursor_key).

        used by the reels endpoint so the frontend can pass back the last id.
        """
        with self._lock:
            if anchor_key is None:
                node = self.head if direction == "next" else self.tail
            else:
                anchor = self._index.get(anchor_key)
                if anchor is None:
                    return [], None
                node = anchor.next if direction == "next" else anchor.prev
            out: List[DLLNode] = []
            while node is not None and len(out) < limit:
                out.append(node)
                node = node.next if direction == "next" else node.prev
            tail_key = out[-1].key if out else None
            return out, tail_key

    # batch construction -------------------------------------------------------
    def hydrate(self, items: Iterable[Tuple[Any, dict]]) -> None:
        """rebuild the list from an ordered iterable of (key, payload)."""
        with self._lock:
            self.head = None
            self.tail = None
            self.current = None
            self._index.clear()
            for key, payload in items:
                self.append(key, payload)

    def keys_in_order(self) -> List[Any]:
        """walk head to tail collecting keys. used by tests and the reels list view."""
        with self._lock:
            out: List[Any] = []
            cursor = self.head
            while cursor is not None:
                out.append(cursor.key)
                cursor = cursor.next
            return out

    def __contains__(self, key: Any) -> bool:
        return key in self._index

    def __len__(self) -> int:
        return self.size


# singleton used by the reels endpoint
_reels = DoublyLinkedList()


def get_reels_list() -> DoublyLinkedList:
    return _reels


def reset_reels_list() -> None:
    _reels.hydrate([])
