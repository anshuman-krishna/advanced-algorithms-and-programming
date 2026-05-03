"""
in memory adjacency list cache for the follow graph.

ref: lab 6 exercise 1 (Graph Representations for Social Networks).
the lab class held both a matrix and a list. claude.md section 5.6 forbids the
matrix at scale (an exabyte for a billion users), so we keep only the list.

the cache is hydrated from the `social.Follow` table on first use and kept
warm by signal handlers. callers should always go through `get_graph()` so the
adjacency list answer is consistent across requests in a single process.
"""

from __future__ import annotations

import threading
from typing import Dict, Iterable, List, Set, Tuple


class FollowGraph:
    """directed adjacency lists for followers and following."""

    def __init__(self) -> None:
        # outgoing edges. who does this user follow.
        self.following: Dict[int, Set[int]] = {}
        # incoming edges. who follows this user.
        self.followers: Dict[int, Set[int]] = {}
        self.num_edges: int = 0
        self._lock = threading.RLock()
        self._hydrated = False

    def _ensure_node(self, user_id: int) -> None:
        if user_id not in self.following:
            self.following[user_id] = set()
        if user_id not in self.followers:
            self.followers[user_id] = set()

    def add_user(self, user_id: int) -> None:
        with self._lock:
            self._ensure_node(user_id)

    def remove_user(self, user_id: int) -> None:
        with self._lock:
            for target in self.following.pop(user_id, set()):
                self.followers.get(target, set()).discard(user_id)
                self.num_edges -= 1
            for source in self.followers.pop(user_id, set()):
                self.following.get(source, set()).discard(user_id)
                self.num_edges -= 1

    def add_edge(self, follower_id: int, target_id: int) -> bool:
        if follower_id == target_id:
            # ref: lab 6 ex 1 implicit no self loop assumption
            return False
        with self._lock:
            self._ensure_node(follower_id)
            self._ensure_node(target_id)
            if target_id in self.following[follower_id]:
                return False
            self.following[follower_id].add(target_id)
            self.followers[target_id].add(follower_id)
            self.num_edges += 1
            return True

    def remove_edge(self, follower_id: int, target_id: int) -> bool:
        with self._lock:
            following = self.following.get(follower_id)
            if not following or target_id not in following:
                return False
            following.discard(target_id)
            self.followers.get(target_id, set()).discard(follower_id)
            self.num_edges -= 1
            return True

    def is_following(self, follower_id: int, target_id: int) -> bool:
        # ref: lab 6 ex 1 are_friends_list, adapted for directed edges
        return target_id in self.following.get(follower_id, set())

    def get_following(self, user_id: int) -> List[int]:
        return sorted(self.following.get(user_id, set()))

    def get_followers(self, user_id: int) -> List[int]:
        return sorted(self.followers.get(user_id, set()))

    def out_degree(self, user_id: int) -> int:
        return len(self.following.get(user_id, set()))

    def in_degree(self, user_id: int) -> int:
        return len(self.followers.get(user_id, set()))

    def degree_distribution(self) -> Dict[int, int]:
        # ref: lab 6 ex 1 degree_distribution. directed total degree.
        dist: Dict[int, int] = {}
        for user_id in self.following:
            deg = self.in_degree(user_id) + self.out_degree(user_id)
            dist[deg] = dist.get(deg, 0) + 1
        return dist

    def graph_density(self) -> float:
        n = len(self.following)
        if n <= 1:
            return 0.0
        # directed graph density, no self loops
        return self.num_edges / (n * (n - 1))

    def num_users(self) -> int:
        return len(self.following)

    def edges(self) -> Iterable[Tuple[int, int]]:
        for source, targets in self.following.items():
            for target in targets:
                yield source, target

    def hydrate(self, user_ids: Iterable[int], edges: Iterable[Tuple[int, int]]) -> None:
        with self._lock:
            self.following.clear()
            self.followers.clear()
            self.num_edges = 0
            for uid in user_ids:
                self._ensure_node(uid)
            for follower_id, target_id in edges:
                self.add_edge(follower_id, target_id)
            self._hydrated = True

    def is_hydrated(self) -> bool:
        return self._hydrated

    def reset(self) -> None:
        with self._lock:
            self.following.clear()
            self.followers.clear()
            self.num_edges = 0
            self._hydrated = False


# process wide singleton. signal handlers update this in place.
_graph = FollowGraph()
_hydration_lock = threading.Lock()


def get_graph() -> FollowGraph:
    return _graph


def hydrate_from_db() -> FollowGraph:
    """populate the singleton from the database. safe to call repeatedly."""
    # local import keeps this module importable without django for unit tests
    from django.contrib.auth import get_user_model

    from social.models import Follow

    with _hydration_lock:
        if _graph.is_hydrated():
            return _graph
        User = get_user_model()
        user_ids = list(User.objects.values_list("id", flat=True))
        edges = list(Follow.objects.values_list("follower_id", "following_id"))
        _graph.hydrate(user_ids, edges)
    return _graph


def ensure_hydrated() -> FollowGraph:
    if not _graph.is_hydrated():
        return hydrate_from_db()
    return _graph
