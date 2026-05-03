"""
binary search tree keyed on user id. mirrors lab 8 exercise 1.

ref: lab 8 exercise 1 (user-search_and_friend-of-friend_suggestion).

claude.md section 5.8 calls for a bst as our primary user index. postgres
already has a btree index on the primary key, so this structure is an
in memory accelerator that lets us reproduce the textbook algorithm and
deliver friend of friend rankings without round tripping the database.

the friends list stored on each node mirrors a partial adjacency list. we
hydrate it from social.Follow at warm up and keep it in sync via signals.
"""

from __future__ import annotations

import threading
from typing import Iterable, List, Optional, Tuple


class UserBSTNode:
    __slots__ = ("user_id", "username", "friends", "left", "right")

    def __init__(self, user_id: int, username: str, friends: Optional[Iterable[int]] = None):
        self.user_id = user_id
        self.username = username
        self.friends: set[int] = set(friends or [])
        self.left: Optional["UserBSTNode"] = None
        self.right: Optional["UserBSTNode"] = None


def insert(root: Optional[UserBSTNode], user_id: int, username: str,
           friends: Optional[Iterable[int]] = None) -> UserBSTNode:
    if root is None:
        return UserBSTNode(user_id, username, friends)
    if user_id < root.user_id:
        root.left = insert(root.left, user_id, username, friends)
    elif user_id > root.user_id:
        root.right = insert(root.right, user_id, username, friends)
    else:
        # duplicate id, refresh metadata only
        root.username = username
        if friends is not None:
            root.friends = set(friends)
    return root


def find(root: Optional[UserBSTNode], target_id: int) -> Optional[UserBSTNode]:
    if root is None or root.user_id == target_id:
        return root
    if target_id < root.user_id:
        return find(root.left, target_id)
    return find(root.right, target_id)


def find_min(node: UserBSTNode) -> UserBSTNode:
    current = node
    while current.left is not None:
        current = current.left
    return current


def delete(root: Optional[UserBSTNode], target_id: int) -> Optional[UserBSTNode]:
    if root is None:
        return None
    if target_id < root.user_id:
        root.left = delete(root.left, target_id)
    elif target_id > root.user_id:
        root.right = delete(root.right, target_id)
    else:
        if root.left is None:
            return root.right
        if root.right is None:
            return root.left
        successor = find_min(root.right)
        root.user_id = successor.user_id
        root.username = successor.username
        root.friends = successor.friends
        root.right = delete(root.right, successor.user_id)
    return root


def inorder(root: Optional[UserBSTNode]) -> List[int]:
    out: List[int] = []
    if root is None:
        return out
    out.extend(inorder(root.left))
    out.append(root.user_id)
    out.extend(inorder(root.right))
    return out


def get_height(root: Optional[UserBSTNode]) -> int:
    if root is None:
        return 0
    return max(get_height(root.left), get_height(root.right)) + 1


def is_balanced(root: Optional[UserBSTNode]) -> bool:
    if root is None:
        return True
    diff = abs(get_height(root.left) - get_height(root.right))
    return diff <= 1 and is_balanced(root.left) and is_balanced(root.right)


def get_leaf_count(root: Optional[UserBSTNode]) -> int:
    if root is None:
        return 0
    if root.left is None and root.right is None:
        return 1
    return get_leaf_count(root.left) + get_leaf_count(root.right)


def suggest_friends(root: Optional[UserBSTNode], target_id: int,
                    max_suggestions: int = 10) -> List[Tuple[int, int]]:
    """
    friend of friend suggestions ranked by mutual count.

    ref: lab 8 ex 1 suggest_friends. returns (user_id, mutual_count) sorted desc.
    """
    target = find(root, target_id)
    if target is None:
        return []
    counts: dict[int, int] = {}
    for friend_id in target.friends:
        friend_node = find(root, friend_id)
        if friend_node is None:
            continue
        for fof_id in friend_node.friends:
            if fof_id == target_id or fof_id in target.friends:
                continue
            counts[fof_id] = counts.get(fof_id, 0) + 1
    ranked = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    return ranked[:max_suggestions]


class UserIndex:
    """thread safe wrapper around the bst root."""

    def __init__(self) -> None:
        self.root: Optional[UserBSTNode] = None
        self._lock = threading.RLock()
        self._hydrated = False

    def insert_user(self, user_id: int, username: str,
                    friends: Optional[Iterable[int]] = None) -> None:
        with self._lock:
            self.root = insert(self.root, user_id, username, friends)

    def remove_user(self, user_id: int) -> None:
        with self._lock:
            self.root = delete(self.root, user_id)

    def get(self, user_id: int) -> Optional[UserBSTNode]:
        with self._lock:
            return find(self.root, user_id)

    def add_friend(self, user_id: int, friend_id: int) -> None:
        with self._lock:
            node = find(self.root, user_id)
            if node is not None:
                node.friends.add(friend_id)

    def remove_friend(self, user_id: int, friend_id: int) -> None:
        with self._lock:
            node = find(self.root, user_id)
            if node is not None:
                node.friends.discard(friend_id)

    def suggest(self, user_id: int, max_suggestions: int = 10) -> List[Tuple[int, int]]:
        with self._lock:
            return suggest_friends(self.root, user_id, max_suggestions)

    def stats(self) -> dict:
        with self._lock:
            return {
                "size": len(inorder(self.root)),
                "height": get_height(self.root),
                "leaf_count": get_leaf_count(self.root),
                "is_balanced": is_balanced(self.root),
            }

    def hydrate(self, users: Iterable[Tuple[int, str]],
                friend_map: dict) -> None:
        with self._lock:
            self.root = None
            for user_id, username in users:
                self.root = insert(
                    self.root, user_id, username, friend_map.get(user_id, set())
                )
            self._hydrated = True

    def is_hydrated(self) -> bool:
        return self._hydrated

    def reset(self) -> None:
        with self._lock:
            self.root = None
            self._hydrated = False


_index = UserIndex()
_hydration_lock = threading.Lock()


def get_index() -> UserIndex:
    return _index


def hydrate_from_db() -> UserIndex:
    """populate the singleton from the database. local imports keep this safe to import in tests."""
    from django.contrib.auth import get_user_model

    from social.models import Follow

    with _hydration_lock:
        if _index.is_hydrated():
            return _index
        User = get_user_model()
        users = list(User.objects.values_list("id", "username"))
        friend_map: dict = {}
        for follower_id, target_id in Follow.objects.values_list(
            "follower_id", "following_id"
        ):
            friend_map.setdefault(follower_id, set()).add(target_id)
        _index.hydrate(users, friend_map)
    return _index


def ensure_hydrated() -> UserIndex:
    if not _index.is_hydrated():
        return hydrate_from_db()
    return _index
