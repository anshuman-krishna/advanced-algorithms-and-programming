"""
weighted engagement scoring.

ref: claude.md phase 3 weighted formula `(0.7 * likes) + (0.3 * recency)`.

both factors are normalized into [0, 1] so the composition is well behaved
across feeds with very different like volumes. likes are squashed with a log
curve so a post with 10000 likes does not eclipse everything else, and
recency is a clamped linear decay over a configurable freshness window.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Iterable, List, Optional, Sequence, Tuple

# weights pulled directly from claude.md
LIKES_WEIGHT = 0.7
RECENCY_WEIGHT = 0.3

# fresh window. older than this contributes 0 recency.
DEFAULT_FRESHNESS_HOURS = 24.0


def _utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def normalize_likes(likes: int, max_likes: int) -> float:
    """log scaled likes normalized against the local max in the feed window."""
    if likes <= 0 or max_likes <= 0:
        return 0.0
    # log1p keeps the curve continuous through zero and dampens runaway hits
    return math.log1p(likes) / math.log1p(max_likes)


def recency_factor(created_at: datetime,
                   now: Optional[datetime] = None,
                   freshness_hours: float = DEFAULT_FRESHNESS_HOURS) -> float:
    """linear decay from 1.0 at posting time down to 0 at the freshness edge."""
    if now is None:
        now = _utc_now()
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    age_hours = (now - created_at).total_seconds() / 3600.0
    if age_hours <= 0:
        return 1.0
    if age_hours >= freshness_hours:
        return 0.0
    return 1.0 - (age_hours / freshness_hours)


def score_post(likes: int, created_at: datetime, max_likes: int,
               now: Optional[datetime] = None,
               freshness_hours: float = DEFAULT_FRESHNESS_HOURS) -> float:
    """blend likes and recency per the phase 3 formula."""
    lk = normalize_likes(likes, max_likes)
    rc = recency_factor(created_at, now=now, freshness_hours=freshness_hours)
    return LIKES_WEIGHT * lk + RECENCY_WEIGHT * rc


def score_batch(posts: Sequence[Tuple[int, int, datetime]],
                now: Optional[datetime] = None,
                freshness_hours: float = DEFAULT_FRESHNESS_HOURS) -> List[Tuple[int, float]]:
    """
    score a batch of posts in linear time.

    ref: lab 1 emphasis on linear time array operations for feed slicing.
    each tuple is (post_id, likes, created_at). returns (post_id, score).
    """
    if now is None:
        now = _utc_now()
    if not posts:
        return []
    max_likes = max((likes for _, likes, _ in posts), default=0)
    out: List[Tuple[int, float]] = []
    for post_id, likes, created_at in posts:
        out.append((post_id, score_post(likes, created_at, max_likes, now=now,
                                         freshness_hours=freshness_hours)))
    return out


def score_breakdown(likes: int, created_at: datetime, max_likes: int,
                    now: Optional[datetime] = None,
                    freshness_hours: float = DEFAULT_FRESHNESS_HOURS) -> dict:
    """
    return a per-component breakdown of the score so the ui can label why
    a post ranked. weights kept here so the frontend can render the same
    tooltip everywhere.
    """
    lk = normalize_likes(likes, max_likes)
    rc = recency_factor(created_at, now=now, freshness_hours=freshness_hours)
    return {
        "likes_normalized": lk,
        "likes_weight": LIKES_WEIGHT,
        "likes_contribution": LIKES_WEIGHT * lk,
        "recency_factor": rc,
        "recency_weight": RECENCY_WEIGHT,
        "recency_contribution": RECENCY_WEIGHT * rc,
        "total": LIKES_WEIGHT * lk + RECENCY_WEIGHT * rc,
    }
