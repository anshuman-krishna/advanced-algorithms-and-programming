"""
reels service layer.

ref: claude.md section 5.3 (lab 3 doubly linked lists for swiping mechanism).
ref: lab 3 ex 1 content_feed_navigation_with_doubly_linked_list. the dll lives in
algorithms/doubly_linked_list.py; this module is the django adapter that hydrates
it from the Post table and exposes typed helpers to the views.

design notes
- one process wide DLL singleton. the head is the newest post so swiping forward
  walks toward older content (matches instagram's reels gesture).
- payload dicts carry the post id, caption, image url, author username, like count
  so the api response does not need a follow-up query per node.
- hydrate_if_empty is the lazy boot: first request after process start scans the db
  once and populates the list. signals (signals.py) keep it warm thereafter.
"""

from __future__ import annotations

import threading
from typing import Any, Dict, List, Optional, Tuple

from django.db.models import Count

from algorithms.doubly_linked_list import DLLNode, get_reels_list, reset_reels_list

from posts.models import Post


_hydration_lock = threading.Lock()
_hydrated = False
# how many of the most recent posts to keep loaded in the dll. anything older
# requires a refresh; this caps the in memory cost while still covering the
# typical scrolling session.
DEFAULT_WINDOW = 200


def _post_payload(post_id: int, *, author_id: int, author_username: str,
                  caption: str, image_url: Optional[str], like_count: int,
                  created_at) -> dict:
    return {
        "id": post_id,
        "author_id": author_id,
        "author_username": author_username,
        "caption": caption,
        "image_url": image_url,
        "like_count": like_count,
        "created_at": created_at.isoformat() if hasattr(created_at, "isoformat") else created_at,
    }


def _payload_from_post(post: Post) -> dict:
    img = post.image.url if post.image else None
    return _post_payload(
        post_id=post.id,
        author_id=post.author_id,
        author_username=getattr(post.author, "username", ""),
        caption=post.caption,
        image_url=img,
        like_count=post.likes.count(),
        created_at=post.created_at,
    )


def hydrate_from_db(window: int = DEFAULT_WINDOW) -> int:
    """
    rebuild the dll from the latest `window` posts.

    ref: lab 3 ex 1 hydrate. used by the management command warm_reels and by
    `reset` debug actions.
    """
    qs = (
        Post.objects
        .select_related("author")
        .annotate(_likes=Count("likes"))
        .order_by("-created_at")[:window]
    )
    items: List[Tuple[int, dict]] = []
    for p in qs:
        payload = _post_payload(
            post_id=p.id,
            author_id=p.author_id,
            author_username=getattr(p.author, "username", ""),
            caption=p.caption,
            image_url=p.image.url if p.image else None,
            like_count=p._likes,
            created_at=p.created_at,
        )
        items.append((p.id, payload))
    dll = get_reels_list()
    dll.hydrate(items)
    return dll.size


def hydrate_if_empty(window: int = DEFAULT_WINDOW) -> int:
    """ref: lab 3 ex 1 lazy boot. only hydrate the first time after process start."""
    global _hydrated
    if _hydrated:
        return get_reels_list().size
    with _hydration_lock:
        if _hydrated:
            return get_reels_list().size
        size = hydrate_from_db(window=window)
        _hydrated = True
        return size


def _node_to_dict(node: DLLNode) -> dict:
    payload = dict(node.payload or {})
    payload["views"] = node.views
    return payload


def page(anchor_key: Optional[Any], direction: str = "next",
         limit: int = 5) -> Tuple[List[dict], Optional[Any]]:
    """ref: lab 3 ex 1 page. cursor pagination across the dll."""
    hydrate_if_empty()
    nodes, next_cursor = get_reels_list().page(anchor_key, direction, limit)
    return [_node_to_dict(n) for n in nodes], next_cursor


def slice_around(post_id: Any, k: int = 3) -> List[dict]:
    """ref: lab 3 ex 1 display_around_current. center on a specific post."""
    hydrate_if_empty()
    dll = get_reels_list()
    if dll.jump_to(post_id) is None:
        return []
    return [_node_to_dict(n) for n in dll.slice_around_cursor(k)]


def jump_to(post_id: Any) -> Optional[dict]:
    """ref: lab 3 ex 1 jump_to."""
    hydrate_if_empty()
    node = get_reels_list().jump_to(post_id)
    return _node_to_dict(node) if node is not None else None


def track_view(post_id: Any) -> Optional[dict]:
    """
    ref: lab 3 ex 1 track_view. set the cursor to post_id then bump views so
    the api can be called with any id without forcing the client to maintain
    cursor state.
    """
    hydrate_if_empty()
    dll = get_reels_list()
    if dll.jump_to(post_id) is None:
        return None
    node = dll.track_view()
    return _node_to_dict(node) if node is not None else None


def most_viewed() -> Optional[dict]:
    """ref: lab 3 ex 1 most_viewed. linear scan, returns highest watched post."""
    hydrate_if_empty()
    node = get_reels_list().most_viewed()
    return _node_to_dict(node) if node is not None else None


def insert_post(post: Post, anchor_key: Optional[Any] = None) -> Optional[dict]:
    """
    ref: lab 3 ex 1 insert_after / append. signal handler entry point.

    if anchor_key is provided we splice in after the anchor; otherwise we put the
    new post at the head so the newest content sits at the top of the feed.
    """
    hydrate_if_empty()
    dll = get_reels_list()
    payload = _payload_from_post(post)
    if anchor_key is not None:
        node = dll.insert_after(anchor_key, post.id, payload)
        if node is not None:
            return _node_to_dict(node)
    if post.id in dll:
        # idempotent re-insert just refreshes the payload
        node = dll.append(post.id, payload)
        return _node_to_dict(node)
    # build a head-first list by hydrating then prepending. since the dll is
    # ordered tail = oldest, we rebuild the index by inserting before head.
    if dll.head is None:
        dll.append(post.id, payload)
    else:
        # manual prepend, mirrors lab 3 ex 1 insert_after but at head
        head = dll.head
        new_node = DLLNode(post.id, payload)
        new_node.next = head
        head.prev = new_node
        dll.head = new_node
        if dll.tail is None:
            dll.tail = new_node
        if dll.current is None:
            dll.current = new_node
        dll._index[post.id] = new_node
    return _node_to_dict(dll._index[post.id])


def remove_post(post_id: Any) -> bool:
    """ref: lab 3 ex 1 remove_story. signal handler on Post delete."""
    hydrate_if_empty()
    return get_reels_list().remove(post_id)


def stats() -> dict:
    dll = get_reels_list()
    return {
        "size": dll.size,
        "head": dll.head.key if dll.head else None,
        "tail": dll.tail.key if dll.tail else None,
        "cursor": dll.current.key if dll.current else None,
        "hydrated": _hydrated,
    }


def force_reset() -> None:
    """clear the in memory list and the hydrated flag. used by tests and ops."""
    global _hydrated
    with _hydration_lock:
        reset_reels_list()
        _hydrated = False
