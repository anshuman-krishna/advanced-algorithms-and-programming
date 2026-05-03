"""
service layer that composes the adjacency list, bst, and set ops.

views in this app and feed ranking in phase 3 should call into this module
instead of touching the algorithm helpers directly.
"""

from __future__ import annotations

from typing import Dict, List, Set, Tuple

from algorithms.follow_graph import ensure_hydrated as ensure_graph
from algorithms.sets_ops import (
    intersection,
    jaccard_similarity,
    mutual_followers,
    suggest_friends_by_set_difference,
)
from algorithms.user_bst import ensure_hydrated as ensure_index


def get_followers(user_id: int) -> List[int]:
    return ensure_graph().get_followers(user_id)


def get_following(user_id: int) -> List[int]:
    return ensure_graph().get_following(user_id)


def is_following(follower_id: int, target_id: int) -> bool:
    return ensure_graph().is_following(follower_id, target_id)


def out_degree(user_id: int) -> int:
    return ensure_graph().out_degree(user_id)


def in_degree(user_id: int) -> int:
    return ensure_graph().in_degree(user_id)


def graph_stats() -> dict:
    g = ensure_graph()
    return {
        "users": g.num_users(),
        "edges": g.num_edges,
        "density": g.graph_density(),
        "degree_distribution": g.degree_distribution(),
    }


def mutual_followers_of(user_a: int, user_b: int) -> Set[int]:
    """ref: lab 2 ex 2 intersection. shared incoming edges."""
    g = ensure_graph()
    return mutual_followers(g.get_followers(user_a), g.get_followers(user_b))


def shared_following_of(user_a: int, user_b: int) -> Set[int]:
    """common targets between two users. used as a similarity signal."""
    g = ensure_graph()
    return intersection(g.get_following(user_a), g.get_following(user_b))


def follower_jaccard(user_a: int, user_b: int) -> float:
    g = ensure_graph()
    return jaccard_similarity(g.get_followers(user_a), g.get_followers(user_b))


def suggest_via_sets(user_id: int) -> Set[int]:
    """ref: lab 2 ex 2 suggest_friends. set based fallback for the bst path."""
    g = ensure_graph()
    following_map: Dict[int, Set[int]] = {
        uid: set(g.get_following(uid)) for uid in g.following.keys()
    }
    return suggest_friends_by_set_difference(
        user_id, g.get_following(user_id), following_map
    )


def suggest_via_bst(user_id: int, max_suggestions: int = 10) -> List[Tuple[int, int]]:
    """ref: lab 8 ex 1 suggest_friends. bst keyed friend of friend ranking."""
    return ensure_index().suggest(user_id, max_suggestions=max_suggestions)


def index_stats() -> dict:
    return ensure_index().stats()


def follow_user(follower_id: int, target_id: int) -> bool:
    """
    create the follow row and propagate to caches via signals.
    returns True if a new edge was created.
    """
    from .models import Follow  # local to avoid circular at import time

    if follower_id == target_id:
        return False
    _, created = Follow.objects.get_or_create(
        follower_id=follower_id, following_id=target_id
    )
    return created


def unfollow_user(follower_id: int, target_id: int) -> int:
    from .models import Follow

    deleted, _ = Follow.objects.filter(
        follower_id=follower_id, following_id=target_id
    ).delete()
    return deleted
