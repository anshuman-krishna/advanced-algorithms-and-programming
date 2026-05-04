"""
content based recommender for the explore page and reels.

ref: lab 2 exercise 2 (jaccard) and exercise 3 (cosine) similarity logic.
ref: claude.md section 5.2 collaborative filtering.

we represent each user by the set of post ids they have liked. two strategies
are exposed:

    jaccard: similar users by overlap of liked posts, surface posts the target
        has not seen yet weighted by overlap.

    cosine: items represented as a binary vector across the universe of users.
        for each candidate post, compute cosine similarity against posts the
        target liked, sum the contributions to rank.

both strategies are expressed in pure python so the module is testable without
django. the django facing service feeds them dictionaries.
"""

from __future__ import annotations

import math
from typing import Dict, Iterable, List, Set, Tuple

from .sets_ops import intersection, jaccard_similarity, union


def _set(value: Iterable[int]) -> Set[int]:
    return value if isinstance(value, set) else set(value)


def jaccard_user_similarity(target_likes: Iterable[int],
                            other_likes: Iterable[int]) -> float:
    return jaccard_similarity(target_likes, other_likes)


def recommend_by_jaccard(target_user_id: int,
                         user_likes: Dict[int, Iterable[int]],
                         max_results: int = 10) -> List[Tuple[int, float]]:
    """
    rank posts the target has not liked, weighted by the jaccard similarity
    of every other user that liked them.
    """
    target = _set(user_likes.get(target_user_id, set()))
    if not target:
        return []
    similarities: Dict[int, float] = {}
    for user_id, likes in user_likes.items():
        if user_id == target_user_id:
            continue
        sim = jaccard_similarity(target, likes)
        if sim > 0:
            similarities[user_id] = sim
    if not similarities:
        return []
    scores: Dict[int, float] = {}
    for user_id, sim in similarities.items():
        for post_id in user_likes.get(user_id, set()):
            if post_id in target:
                continue
            scores[post_id] = scores.get(post_id, 0.0) + sim
    ranked = sorted(scores.items(), key=lambda pair: pair[1], reverse=True)
    return ranked[:max_results]


def cosine_post_similarity(post_a_users: Iterable[int],
                           post_b_users: Iterable[int]) -> float:
    """
    cosine over the binary co-like vectors. derived from lab 2 ex 3 cosine
    formula; here the vectors are characteristic functions of the user set,
    so the dot product equals |A inter B| and norm_a = sqrt(|A|).
    """
    a = _set(post_a_users)
    b = _set(post_b_users)
    if not a or not b:
        return 0.0
    inter = len(intersection(a, b))
    return inter / (math.sqrt(len(a)) * math.sqrt(len(b)))


def recommend_by_cosine(target_user_id: int,
                        user_likes: Dict[int, Iterable[int]],
                        post_likes: Dict[int, Iterable[int]],
                        max_results: int = 10) -> List[Tuple[int, float]]:
    """
    item to item cosine. for every candidate post (not already liked), score
    it as the sum of cosine similarities against posts the target has liked.
    """
    target = _set(user_likes.get(target_user_id, set()))
    if not target:
        return []
    scores: Dict[int, float] = {}
    for candidate_id, candidate_users in post_likes.items():
        if candidate_id in target:
            continue
        score = 0.0
        for liked_id in target:
            score += cosine_post_similarity(candidate_users, post_likes.get(liked_id, set()))
        if score > 0:
            scores[candidate_id] = score
    ranked = sorted(scores.items(), key=lambda pair: pair[1], reverse=True)
    return ranked[:max_results]
