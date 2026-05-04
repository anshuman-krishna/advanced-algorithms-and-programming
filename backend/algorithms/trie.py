"""
prefix tree for username and hashtag autocomplete.

ref: lab 8 exercise 3 (prefix_and_range_trees). same trie shape; we generalize
the payload so a single class serves both username -> user_id and hashtag ->
post_count lookups. weights drive autocomplete ranking.
"""

from __future__ import annotations

import threading
from typing import Dict, Iterable, List, Optional, Tuple


class TrieNode:
    __slots__ = ("children", "is_end", "key", "payload", "weight")

    def __init__(self) -> None:
        self.children: Dict[str, "TrieNode"] = {}
        self.is_end: bool = False
        self.key: Optional[str] = None
        self.payload: Optional[object] = None
        self.weight: float = 0.0


class Trie:
    def __init__(self) -> None:
        self.root = TrieNode()
        self._lock = threading.RLock()
        self._hydrated = False

    def insert(self, key: str, payload: Optional[object] = None,
               weight: float = 1.0) -> None:
        if not key:
            return
        with self._lock:
            node = self.root
            for ch in key:
                if ch not in node.children:
                    node.children[ch] = TrieNode()
                node = node.children[ch]
            node.is_end = True
            node.key = key
            node.payload = payload
            node.weight = weight

    def search(self, key: str) -> Optional[object]:
        with self._lock:
            node = self.root
            for ch in key:
                if ch not in node.children:
                    return None
                node = node.children[ch]
            return node.payload if node.is_end else None

    def starts_with(self, prefix: str) -> bool:
        with self._lock:
            node = self.root
            for ch in prefix:
                if ch not in node.children:
                    return False
                node = node.children[ch]
            return True

    def autocomplete(self, prefix: str, max_results: int = 10) -> List[Tuple[str, object, float]]:
        """
        return up to max_results (key, payload, weight) tuples sorted by weight desc.

        ref: lab 8 ex 3 autocomplete. we collect every leaf under the prefix and
        then sort by weight so the most popular completions float to the top.
        """
        results: List[Tuple[str, object, float]] = []
        with self._lock:
            node = self.root
            for ch in prefix:
                if ch not in node.children:
                    return results
                node = node.children[ch]
            self._collect(node, results)
        results.sort(key=lambda triple: triple[2], reverse=True)
        return results[:max_results]

    def _collect(self, node: TrieNode, out: List[Tuple[str, object, float]]) -> None:
        if node.is_end and node.key is not None:
            out.append((node.key, node.payload, node.weight))
        for child in node.children.values():
            self._collect(child, out)

    def increment_weight(self, key: str, delta: float = 1.0) -> None:
        with self._lock:
            node = self.root
            for ch in key:
                if ch not in node.children:
                    return
                node = node.children[ch]
            if node.is_end:
                node.weight += delta

    def delete(self, key: str) -> None:
        with self._lock:
            self._delete(self.root, key, 0)

    def _delete(self, node: TrieNode, key: str, index: int) -> bool:
        if index == len(key):
            if not node.is_end:
                return False
            node.is_end = False
            node.key = None
            node.payload = None
            node.weight = 0.0
            return len(node.children) == 0
        ch = key[index]
        if ch not in node.children:
            return False
        should_remove = self._delete(node.children[ch], key, index + 1)
        if should_remove:
            del node.children[ch]
            return len(node.children) == 0 and not node.is_end
        return False

    def hydrate(self, items: Iterable[Tuple[str, object, float]]) -> None:
        with self._lock:
            self.root = TrieNode()
            for key, payload, weight in items:
                self.insert(key, payload=payload, weight=weight)
            self._hydrated = True

    def is_hydrated(self) -> bool:
        return self._hydrated

    def reset(self) -> None:
        with self._lock:
            self.root = TrieNode()
            self._hydrated = False


# two singletons, one per surface
_user_trie = Trie()
_hashtag_trie = Trie()
_lock = threading.Lock()


def get_user_trie() -> Trie:
    return _user_trie


def get_hashtag_trie() -> Trie:
    return _hashtag_trie


def hydrate_user_trie() -> Trie:
    from django.contrib.auth import get_user_model

    User = get_user_model()
    with _lock:
        if _user_trie.is_hydrated():
            return _user_trie
        rows = User.objects.values_list("username", "id")
        _user_trie.hydrate(((u, uid, 1.0) for u, uid in rows))
    return _user_trie


def hydrate_hashtag_trie() -> Trie:
    from search.models import Hashtag

    with _lock:
        if _hashtag_trie.is_hydrated():
            return _hashtag_trie
        rows = Hashtag.objects.values_list("name", "id", "post_count")
        _hashtag_trie.hydrate(((name, hid, float(count)) for name, hid, count in rows))
    return _hashtag_trie


def ensure_user_trie() -> Trie:
    if not _user_trie.is_hydrated():
        return hydrate_user_trie()
    return _user_trie


def ensure_hashtag_trie() -> Trie:
    if not _hashtag_trie.is_hydrated():
        return hydrate_hashtag_trie()
    return _hashtag_trie
