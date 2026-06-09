"""
analytics service layer over the segment tree primitive.

ref: claude.md section 5.8 (lab 8 segment trees for activity analytics).
ref: lab 8 ex 3 prefix and range trees blueprint, applied to per-user daily likes.

we keep one DailySegmentTree per user, lazily created on first access. each tree
covers a sliding `WINDOW_DAYS` window ending today, so range queries beyond that
window simply clamp. this matches the spec: "counting total likes over a
specific date range".

design notes
- a process-wide registry maps user_id -> DailySegmentTree. signals push +1 on
  Like create and -1 on Like delete so the in-memory tree stays consistent with
  the database.
- on first access we replay the user's existing likes from the db so the tree
  is correct even after a cold start. subsequent calls hit the in-memory data.
- the trees are recreated lazily; if the process restarts every cache rebuilds
  on demand.
"""

from __future__ import annotations

import threading
from datetime import date, timedelta
from typing import Dict, List, Optional

from django.utils import timezone

from algorithms.segment_tree import DailySegmentTree


WINDOW_DAYS = 365

_trees: Dict[int, DailySegmentTree] = {}
# a second, parallel registry of segment trees counting comments received per day
# on each user's posts. same lab 8 ex 3 structure, different event source.
_comment_trees: Dict[int, DailySegmentTree] = {}
_lock = threading.RLock()


def _origin() -> date:
    today = timezone.now().date()
    return today - timedelta(days=WINDOW_DAYS - 1)


def _build_tree(user_id: int) -> DailySegmentTree:
    """ref: lab 8 ex 3 build. replay all likes inside the window into the tree."""
    from posts.models import Like

    origin = _origin()
    tree = DailySegmentTree(origin, window_days=WINDOW_DAYS)
    qs = (
        Like.objects
        .filter(post__author_id=user_id, created_at__date__gte=origin)
        .values_list("created_at", flat=True)
    )
    for ts in qs:
        tree.add(ts.date(), 1)
    return tree


def get_tree(user_id: int) -> DailySegmentTree:
    """lazy factory. ref: lab 8 ex 3 the tree is per-key analytical structure."""
    with _lock:
        tree = _trees.get(user_id)
        if tree is None:
            tree = _build_tree(user_id)
            _trees[user_id] = tree
        return tree


def record_like(user_id: int, day: Optional[date] = None) -> bool:
    """signal entry point on Like create. returns True if inside window."""
    tree = get_tree(user_id)
    return tree.add(day or timezone.now().date(), 1)


def revoke_like(user_id: int, day: Optional[date] = None) -> bool:
    """signal entry point on Like delete. ref: lab 8 ex 3 point_update with negative delta."""
    tree = get_tree(user_id)
    # subtraction is just point_update with negative delta on a sum tree
    tree.tree.point_update(tree._index(day or timezone.now().date()), -1)
    return True


def likes_in_range(user_id: int, start: date, end_inclusive: date) -> float:
    """ref: lab 8 ex 3 range_sum."""
    return get_tree(user_id).query(start, end_inclusive)


def peak_day_in_range(user_id: int, start: date, end_inclusive: date) -> float:
    """ref: lab 8 ex 3 range_max via DailySegmentTree.peak."""
    return get_tree(user_id).peak(start, end_inclusive)


def daily_series(user_id: int) -> List[float]:
    """leaves of the tree in date order. powers the histogram on the client."""
    return get_tree(user_id).daily_series()


# comments per day on the user's posts, mirroring the likes tree above.

def _build_comment_tree(user_id: int) -> DailySegmentTree:
    """ref: lab 8 ex 3 build. replay every comment on this user's posts."""
    from posts.models import Comment

    origin = _origin()
    tree = DailySegmentTree(origin, window_days=WINDOW_DAYS)
    qs = (
        Comment.objects
        .filter(post__author_id=user_id, created_at__date__gte=origin)
        .values_list("created_at", flat=True)
    )
    for ts in qs:
        tree.add(ts.date(), 1)
    return tree


def get_comment_tree(user_id: int) -> DailySegmentTree:
    with _lock:
        tree = _comment_trees.get(user_id)
        if tree is None:
            tree = _build_comment_tree(user_id)
            _comment_trees[user_id] = tree
        return tree


def record_comment(user_id: int, day: Optional[date] = None) -> bool:
    """signal entry point on Comment create. user_id is the post author."""
    tree = get_comment_tree(user_id)
    return tree.add(day or timezone.now().date(), 1)


def revoke_comment(user_id: int, day: Optional[date] = None) -> bool:
    """signal entry point on Comment delete. ref: lab 8 ex 3 negative point_update."""
    tree = get_comment_tree(user_id)
    tree.tree.point_update(tree._index(day or timezone.now().date()), -1)
    return True


def comments_in_range(user_id: int, start: date, end_inclusive: date) -> float:
    return get_comment_tree(user_id).query(start, end_inclusive)


def peak_comment_day_in_range(user_id: int, start: date, end_inclusive: date) -> float:
    return get_comment_tree(user_id).peak(start, end_inclusive)


def comment_daily_series(user_id: int) -> List[float]:
    return get_comment_tree(user_id).daily_series()


def reset() -> None:
    """ops only; drops every cached tree so the next read rebuilds from db."""
    with _lock:
        _trees.clear()
        _comment_trees.clear()


def stats() -> dict:
    with _lock:
        return {
            "users_cached": len(_trees),
            "comment_users_cached": len(_comment_trees),
            "window_days": WINDOW_DAYS,
            "origin": _origin().isoformat(),
        }
