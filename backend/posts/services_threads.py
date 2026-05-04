"""
adapter that turns Comment rows into the algorithms/comment_thread CommentNode tree.

ref: claude.md phase 5. lab 4 ex 1, ex 2, ex 3.
"""

from __future__ import annotations

from typing import List, Optional

from django.db.models import Count

from algorithms.comment_thread import (
    CommentNode,
    build_thread,
    ensure_recursion_limit,
    prune_deleted,
    thread_summary,
)

from .models import Comment, Post


def _rows_for_post(post_id: int) -> List[dict]:
    qs = (
        Comment.objects
        .filter(post_id=post_id)
        .annotate(annotated_likes=Count("id"))  # placeholder until reactions land
        .values("id", "author_id", "content", "parent_id", "is_deleted", "created_at")
    )
    return [
        {
            "id": r["id"],
            "user_id": r["author_id"],
            "content": r["content"],
            "parent_id": r["parent_id"],
            "is_deleted": r["is_deleted"],
            "likes": 0,
            "created_at": r["created_at"],
        }
        for r in qs
    ]


def thread_for_post(post_id: int, prune: bool = True) -> List[dict]:
    """
    fetch every comment on the post, fold into a recursive tree, and serialize.

    ref: lab 4 ex 1 build, ex 2 aggregation, ex 3 explicit stack hints (we set
    a higher recursion limit to make sure deep threads do not crash a worker).
    """
    ensure_recursion_limit(min_limit=10000)
    roots: List[CommentNode] = build_thread(_rows_for_post(post_id))
    if prune:
        kept: List[CommentNode] = []
        for root in roots:
            pruned = prune_deleted(root)
            if pruned is not None:
                kept.append(pruned)
        roots = kept
    return [r.to_dict() for r in roots]


def thread_metrics(post_id: int) -> dict:
    """count, max depth, total likes for the post's comment tree."""
    roots: List[CommentNode] = build_thread(_rows_for_post(post_id))
    if not roots:
        return {"count": 0, "max_depth": 0, "total_likes": 0, "roots": 0}
    summed = {"count": 0, "max_depth": 0, "total_likes": 0}
    for root in roots:
        s = thread_summary(root)
        summed["count"] += s["count"]
        summed["max_depth"] = max(summed["max_depth"], s["max_depth"])
        summed["total_likes"] += s["total_likes"]
    summed["roots"] = len(roots)
    return summed
