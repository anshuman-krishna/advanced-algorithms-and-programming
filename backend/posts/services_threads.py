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
    contains_keyword,
    ensure_recursion_limit,
    find_deepest_reply,
    flatten_iterative,
    prune_deleted,
    search_by_user,
    thread_summary,
    total_engagement,
)

from .models import Comment, Post


def _rows_for_post(post_id: int) -> List[dict]:
    qs = (
        Comment.objects
        .filter(post_id=post_id)
        .annotate(annotated_likes=Count("comment_likes"))
        .values("id", "author_id", "content", "parent_id", "is_deleted",
                "created_at", "annotated_likes")
    )
    return [
        {
            "id": r["id"],
            "user_id": r["author_id"],
            "content": r["content"],
            "parent_id": r["parent_id"],
            "is_deleted": r["is_deleted"],
            "likes": r["annotated_likes"] or 0,
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
        return {"count": 0, "max_depth": 0, "total_likes": 0,
                "engagement": 0.0, "roots": 0}
    summed = {"count": 0, "max_depth": 0, "total_likes": 0, "engagement": 0.0}
    for root in roots:
        s = thread_summary(root)
        summed["count"] += s["count"]
        summed["max_depth"] = max(summed["max_depth"], s["max_depth"])
        summed["total_likes"] += s["total_likes"]
        # ref: lab 4 ex 2 divide and conquer engagement aggregator
        summed["engagement"] += total_engagement(root)
    summed["roots"] = len(roots)
    return summed


def search_thread_by_user(post_id: int, user_id: int) -> List[dict]:
    """ref: lab 4 ex 1 search_by_user, executed across every root in the thread."""
    ensure_recursion_limit(min_limit=10000)
    roots: List[CommentNode] = build_thread(_rows_for_post(post_id))
    out: List[CommentNode] = []
    for root in roots:
        out.extend(search_by_user(user_id, root))
    return [{"id": n.comment_id, "user_id": n.user_id, "content": n.content,
             "likes": n.likes, "parent_id": n.parent_id} for n in out]


def search_thread_by_keyword(post_id: int, keyword: str) -> List[dict]:
    """ref: lab 4 ex 1 contains_keyword, but returns matching nodes instead of bool."""
    ensure_recursion_limit(min_limit=10000)
    needle = (keyword or "").lower()
    if not needle:
        return []
    roots: List[CommentNode] = build_thread(_rows_for_post(post_id))
    matches: List[CommentNode] = []
    for root in roots:
        for node in flatten_iterative(root):
            if not node.is_deleted and needle in (node.content or "").lower():
                matches.append(node)
    return [{"id": n.comment_id, "user_id": n.user_id, "content": n.content,
             "likes": n.likes, "parent_id": n.parent_id} for n in matches]


def deepest_branch_depth(post_id: int) -> int:
    """ref: lab 4 ex 1 find_deepest_reply across all roots."""
    roots: List[CommentNode] = build_thread(_rows_for_post(post_id))
    if not roots:
        return 0
    return max(find_deepest_reply(root) for root in roots)


def thread_count(post_id: int) -> int:
    """
    iterative count of every comment under a post.

    ref: lab 4 ex 3 count_iterative. cheaper than thread_for_post since we do
    not allocate the dict tree, just the flat node list.
    """
    from algorithms.comment_thread import count_iterative

    roots: List[CommentNode] = build_thread(_rows_for_post(post_id))
    return sum(count_iterative(root) for root in roots)


def thread_engagement(post_id: int, score: str = "likes") -> dict:
    """
    swap the lab 4 ex 2 score function on the fly.

    score=likes  -> like count per node, deleted nodes contribute zero
    score=recency -> exponential decay by age, fresh comments dominate
    """
    import math
    from datetime import datetime, timezone as dt_timezone

    roots: List[CommentNode] = build_thread(_rows_for_post(post_id))
    if not roots:
        return {"score": score, "engagement": 0.0, "roots": 0}

    if score == "recency":
        now = datetime.now(dt_timezone.utc)

        def score_fn(node: CommentNode) -> float:
            if node.is_deleted or node.created_at is None:
                return 0.0
            try:
                age_hours = max(0.0, (now - node.created_at).total_seconds() / 3600.0)
            except TypeError:
                return 1.0
            # half life of 24h
            return math.exp(-age_hours / 24.0)
    else:
        score_fn = None  # default in total_engagement (likes)

    total = 0.0
    for root in roots:
        total += total_engagement(root, score_fn)
    return {"score": score, "engagement": total, "roots": len(roots)}
