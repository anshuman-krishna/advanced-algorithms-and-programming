"""
feed generation service.

home feed: for a given user, fetch posts from authors they follow within a
recent window, score them via the phase 3 weighted formula, push them through
the linked list priority queue (lab 3 ex 3), and return a paginated slice.

trending feed: pull a global window of recent posts, score them, push into
the singleton max heap (lab 8 ex 2), and return the top k.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Iterable, List, Optional

from django.db.models import Count
from django.utils import timezone

from algorithms.doubly_linked_list import get_reels_list
from algorithms.max_heap import get_trending_heap, hydrate_trending, is_hydrated, mark_dirty
from algorithms.priority_queue import FeedPriorityQueue
from algorithms.scoring import score_batch, score_breakdown, score_post

# how far back to look when materializing a feed window
DEFAULT_WINDOW_HOURS = 72
DEFAULT_TRENDING_LIMIT = 50


def _post_window_qs(hours: int = DEFAULT_WINDOW_HOURS, author_ids: Optional[Iterable[int]] = None):
    from posts.models import Post  # local import to keep this module test friendly

    cutoff = timezone.now() - timedelta(hours=hours)
    qs = (
        Post.objects.filter(created_at__gte=cutoff)
        .annotate(annotated_likes=Count("likes"))
        .select_related("author")
    )
    if author_ids is not None:
        qs = qs.filter(author_id__in=list(author_ids))
    return qs.order_by("-created_at")


def build_home_feed(user_id: int,
                    offset: int = 0,
                    limit: int = 20,
                    window_hours: int = DEFAULT_WINDOW_HOURS) -> List[dict]:
    """
    materialize the personalized timeline for a user.

    ref: lab 3 ex 3 priority queue, lab 1 linear time slicing.
    """
    from social.services import get_following

    following_ids = get_following(user_id)
    if not following_ids:
        # cold start: surface the user's own recent posts so the feed is not empty
        following_ids = [user_id]

    posts = list(_post_window_qs(hours=window_hours, author_ids=following_ids))
    if not posts:
        return []

    triples = [(p.id, p.annotated_likes, p.created_at) for p in posts]
    scored = dict(score_batch(triples))
    max_likes = max((p.annotated_likes for p in posts), default=0)

    pq = FeedPriorityQueue()
    posts_by_id = {p.id: p for p in posts}
    for post_id, score in scored.items():
        post = posts_by_id[post_id]
        breakdown = score_breakdown(post.annotated_likes, post.created_at, max_likes)
        pq.insert(
            post_id,
            score,
            payload={
                "author_id": post.author_id,
                "author_username": post.author.username,
                "caption": post.caption,
                "image": post.image.url if post.image else None,
                "likes": post.annotated_likes,
                "created_at": post.created_at.isoformat(),
                "score_breakdown": breakdown,
            },
        )
    return pq.slice(offset, limit)


def build_trending_feed(k: int = 10,
                        window_hours: int = DEFAULT_WINDOW_HOURS,
                        force: bool = False) -> List[dict]:
    """
    top k trending posts via the singleton max heap.

    ref: lab 8 ex 2 get_top_k.
    """
    if force or not is_hydrated():
        posts = list(_post_window_qs(hours=window_hours))
        triples = [(p.id, p.annotated_likes, p.created_at) for p in posts]
        scores = dict(score_batch(triples))
        items = []
        for p in posts:
            items.append((
                p.id,
                scores[p.id],
                {
                    "author_id": p.author_id,
                    "author_username": p.author.username,
                    "caption": p.caption,
                    "image": p.image.url if p.image else None,
                    "likes": p.annotated_likes,
                    "created_at": p.created_at.isoformat(),
                },
            ))
        hydrate_trending(items)

    heap = get_trending_heap()
    out: List[dict] = []
    for node in heap.get_top_k(k):
        score, post_id, payload = node
        entry = {"post_id": post_id, "score": score}
        entry.update(payload or {})
        out.append(entry)
    return out


def invalidate_trending() -> None:
    """called by signals when likes or posts change."""
    mark_dirty()


# reels feed (phase 5) ---------------------------------------------------------

def _hydrate_reels_dll(window_hours: int = DEFAULT_WINDOW_HOURS):
    """
    rebuild the reels doubly linked list from the most recent posts.

    ref: claude.md phase 5. lab 3 ex 1 doubly linked list. we order by
    -created_at so swiping forward walks back in time, which matches typical
    reels semantics.
    """
    posts = list(_post_window_qs(hours=window_hours))
    items = [
        (
            p.id,
            {
                "post_id": p.id,
                "author_id": p.author_id,
                "author_username": p.author.username,
                "caption": p.caption,
                "image": p.image.url if p.image else None,
                "likes": p.annotated_likes,
                "created_at": p.created_at.isoformat(),
            },
        )
        for p in posts
    ]
    dll = get_reels_list()
    dll.hydrate(items)
    return dll


def build_reels_page(cursor: Optional[int] = None,
                     direction: str = "next",
                     limit: int = 5,
                     window_hours: int = DEFAULT_WINDOW_HOURS,
                     force: bool = False) -> dict:
    """
    cursor paginated reels via the doubly linked list.

    ref: lab 3 ex 1 move_forward / move_backward / insert_after. we use the
    DoublyLinkedList.page helper so both directions cost O(limit) regardless
    of how deep into the feed the user has swiped.
    """
    dll = get_reels_list()
    if force or len(dll) == 0:
        dll = _hydrate_reels_dll(window_hours=window_hours)

    if cursor is None:
        nodes, next_cursor = dll.page(anchor_key=None, direction=direction, limit=limit)
        # include the head/tail node itself when no cursor was supplied
        head_payload = dll.head.payload if dll.head else None
        if direction == "next" and head_payload is not None:
            nodes = [dll.head] + nodes[: max(0, limit - 1)]
            next_cursor = nodes[-1].key if nodes else None
        if direction == "prev" and dll.tail is not None:
            nodes = [dll.tail] + nodes[: max(0, limit - 1)]
            next_cursor = nodes[-1].key if nodes else None
    else:
        nodes, next_cursor = dll.page(anchor_key=cursor, direction=direction, limit=limit)

    if dll.current is None and dll.head is not None:
        dll.current = dll.head

    return {
        "results": [n.payload for n in nodes],
        "next_cursor": next_cursor,
        "size": len(dll),
        "direction": direction,
    }


def reels_track_view(post_id: int) -> int:
    """ref: lab 3 ex 1 track_view. returns the new view counter or 0 when unknown."""
    dll = get_reels_list()
    node = dll.jump_to(post_id)
    if node is None:
        return 0
    dll.track_view()
    return node.views


def reels_most_viewed() -> Optional[dict]:
    """ref: lab 3 ex 1 most_viewed."""
    node = get_reels_list().most_viewed()
    if node is None:
        return None
    return {"post_id": node.key, "views": node.views, **(node.payload or {})}


def invalidate_reels() -> None:
    """called by signals when posts change. rebuild on next read."""
    get_reels_list().hydrate([])
