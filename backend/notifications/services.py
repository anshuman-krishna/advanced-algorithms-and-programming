"""
notification service: push rows into the queue, drain into the database.

ref: claude.md phase 5 (background notification queue for likes and comments).
ref: lab 3 ex 2 NotificationQueue.

flow
- signal handler builds a payload dict and calls `enqueue_event`.
- a drain pass (called inline at request time and from a management command)
  pulls events off the queue and creates Notification rows.

we deliberately keep the queue in memory: the persisted Notification rows are
the source of truth for the api list view, the queue is just the lab 3 buffer
that decouples writes from delivery.
"""

from __future__ import annotations

from typing import Iterable, List, Optional

from django.utils import timezone

from algorithms.notification_queue import get_queue

from .models import Notification


def enqueue_event(*, recipient_id: int, actor_id: int, kind: str,
                  post_id: Optional[int] = None,
                  comment_id: Optional[int] = None,
                  is_priority: bool = False) -> None:
    """called by signal handlers. ref: lab 3 ex 2 enqueue / priority_enqueue."""
    if recipient_id == actor_id:
        # do not notify yourself
        return
    payload = {
        "recipient_id": recipient_id,
        "actor_id": actor_id,
        "kind": kind,
        "post_id": post_id,
        "comment_id": comment_id,
        "is_priority": is_priority,
    }
    queue = get_queue()
    if is_priority:
        queue.priority_enqueue(payload)
    else:
        queue.enqueue(payload)


def drain(max_events: int = 100) -> List[Notification]:
    """
    pop up to max_events from the queue and persist them.

    ref: lab 3 ex 2 batch_process. the handler creates a Notification row per
    event so the list endpoint serves stable data.
    """
    queue = get_queue()
    drained = queue.batch_process(max_events)
    if not drained:
        return []
    objs = [
        Notification(
            recipient_id=item["recipient_id"],
            actor_id=item["actor_id"],
            kind=item["kind"],
            post_id=item.get("post_id"),
            comment_id=item.get("comment_id"),
            is_priority=bool(item.get("is_priority")),
            delivered_at=timezone.now(),
        )
        for item in drained
    ]
    Notification.objects.bulk_create(objs)
    return objs


def pending_count() -> int:
    return len(get_queue())


def queue_stats() -> dict:
    return get_queue().stats()
