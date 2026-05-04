"""
fifo notification queue with a priority front lane.

ref: claude.md section 5.3 (lab 3 queues).
ref: lab 3 exercise 2 (activity_feed_processing_with_stacks_and_queues) for the
NotificationQueue.enqueue, dequeue, priority_enqueue, batch_process semantics.

implementation notes
- backed by collections.deque so enqueue and dequeue are O(1) at both ends.
  the lab implementation used a python list with pop(0), which is O(n); we
  keep the same interface but pay only O(1) per call.
- a separate `processed_log` records what has been delivered for the recent
  activity stack the ui surfaces.
- thread safe (RLock) so signal handlers and background drainers don't race.
"""

from __future__ import annotations

import threading
from collections import deque
from typing import Any, Callable, Deque, List, Optional, Tuple


class NotificationQueue:
    def __init__(self) -> None:
        self._queue: Deque[dict] = deque()
        self._processed_log: List[dict] = []
        self._lock = threading.RLock()

    # core fifo
    def enqueue(self, notification: dict) -> None:
        """ref: lab 3 ex 2 enqueue. appends to the right of the deque."""
        with self._lock:
            self._queue.append(notification)

    def dequeue(self) -> Optional[dict]:
        """ref: lab 3 ex 2 dequeue. returns None on empty rather than raising."""
        with self._lock:
            if not self._queue:
                return None
            return self._queue.popleft()

    # priority lane
    def priority_enqueue(self, notification: dict) -> None:
        """ref: lab 3 ex 2 priority_enqueue. front of the queue."""
        with self._lock:
            self._queue.appendleft(notification)

    def batch_process(self, k: int,
                      handler: Optional[Callable[[dict], None]] = None) -> List[dict]:
        """
        drain up to k items, return them, and optionally invoke a handler per item.

        ref: lab 3 ex 2 FeedProcessor.batch_process.
        """
        out: List[dict] = []
        with self._lock:
            for _ in range(max(0, k)):
                if not self._queue:
                    break
                item = self._queue.popleft()
                out.append(item)
                self._processed_log.append(item)
        if handler is not None:
            for item in out:
                handler(item)
        return out

    def peek(self) -> Optional[dict]:
        with self._lock:
            return self._queue[0] if self._queue else None

    def pending(self) -> List[dict]:
        with self._lock:
            return list(self._queue)

    def processed(self) -> List[dict]:
        with self._lock:
            return list(self._processed_log)

    def stats(self) -> dict:
        with self._lock:
            return {
                "pending": len(self._queue),
                "processed": len(self._processed_log),
            }

    def clear(self) -> None:
        with self._lock:
            self._queue.clear()
            self._processed_log.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._queue)


# singleton for the running process. signal handlers push, the consumer drains.
_queue = NotificationQueue()


def get_queue() -> NotificationQueue:
    return _queue


# for tests that need a fresh slate
def reset_queue() -> None:
    _queue.clear()
