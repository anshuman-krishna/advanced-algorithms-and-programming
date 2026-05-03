"""
set operations for social network queries.

ref: lab 2 exercise 2 (mutual_friends_detection_using_sets) for intersection,
difference, union, jaccard_similarity, and the suggest_friends helper.
ref: lab 2 exercise 4 (mutual_followers_matrix) for the mutual followers
semantic (a pair where both follow each other).

we keep python primitives only here so the module stays usable from unit
tests without django installed.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Set, Tuple


def intersection(set1: Iterable[int], set2: Iterable[int]) -> Set[int]:
    s1 = set(set1)
    s2 = set(set2)
    result: Set[int] = set()
    for element in s1:
        if element in s2:
            result.add(element)
    return result


def difference(set1: Iterable[int], set2: Iterable[int]) -> Set[int]:
    s2 = set(set2)
    result: Set[int] = set()
    for element in set1:
        if element not in s2:
            result.add(element)
    return result


def union(set1: Iterable[int], set2: Iterable[int]) -> Set[int]:
    result: Set[int] = set()
    for element in set1:
        result.add(element)
    for element in set2:
        result.add(element)
    return result


def jaccard_similarity(set1: Iterable[int], set2: Iterable[int]) -> float:
    s1 = set(set1)
    s2 = set(set2)
    inter = len(s1 & s2)
    uni = len(s1 | s2)
    if uni == 0:
        return 0.0
    return inter / uni


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """ref: lab 2 ex 3 cosine_similarity."""
    if len(vec_a) != len(vec_b):
        raise ValueError("vectors must share length")
    dot = 0.0
    norm_a = 0.0
    norm_b = 0.0
    for i in range(len(vec_a)):
        dot += vec_a[i] * vec_b[i]
        norm_a += vec_a[i] * vec_a[i]
        norm_b += vec_b[i] * vec_b[i]
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / ((norm_a ** 0.5) * (norm_b ** 0.5))


def mutual_followers(
    followers_of_a: Iterable[int], followers_of_b: Iterable[int]
) -> Set[int]:
    """users that follow both a and b. classic intersection."""
    return intersection(followers_of_a, followers_of_b)


def mutual_following(
    following_of_a: Iterable[int], following_of_b: Iterable[int]
) -> Set[int]:
    """users that both a and b follow."""
    return intersection(following_of_a, following_of_b)


def mutual_pairs(
    following_map: Dict[int, Iterable[int]],
) -> List[Tuple[int, int]]:
    """
    pairs where each user follows the other.

    ref: lab 2 ex 4 find_mutual_follows. we return canonical (a, b) with a < b
    so the result is deduplicated.
    """
    pairs: List[Tuple[int, int]] = []
    seen: Set[Tuple[int, int]] = set()
    for user_id, targets in following_map.items():
        for target_id in targets:
            if user_id == target_id:
                continue
            if user_id in following_map.get(target_id, set()):
                key = (min(user_id, target_id), max(user_id, target_id))
                if key not in seen:
                    seen.add(key)
                    pairs.append(key)
    return pairs


def suggest_friends_by_set_difference(
    user_id: int,
    user_following: Iterable[int],
    following_map: Dict[int, Iterable[int]],
) -> Set[int]:
    """
    friends of friends, excluding self and direct connections.

    ref: lab 2 ex 2 suggest_friends. operates on adjacency dictionaries.
    """
    user_following_set = set(user_following)
    suggestions: Set[int] = set()
    for friend_id in user_following_set:
        for candidate in following_map.get(friend_id, set()):
            if candidate == user_id:
                continue
            if candidate in user_following_set:
                continue
            suggestions.add(candidate)
    return suggestions
