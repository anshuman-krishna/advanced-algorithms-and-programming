"""
recursive comment thread structure for nested replies.

ref: claude.md section 5.4 (lab 4 recursive algorithms).
ref: lab 4 exercise 1 (recursive_comment_thread_traversal) for the CommentNode
shape, count_total_comments, total_likes, find_deepest_reply, search_by_user,
contains_keyword, delete_comment.
ref: lab 4 exercise 3 (recursion to iteration with explicit stack) for the
flatten_iterative and count_iterative pair, used so we never blow the python
stack on threads deeper than the recursion limit.
ref: lab 4 exercise 2 (divide and conquer aggregation) for the post order
total_engagement aggregator (sum at each subtree).

we keep this module independent of django so the algorithm tests can import it
straight up. the django adapter lives in posts/services_threads.py and turns
Comment rows into CommentNode trees.
"""

from __future__ import annotations

import sys
from typing import Callable, Dict, Iterable, List, Optional


class CommentNode:
    __slots__ = ("comment_id", "user_id", "content", "created_at", "likes",
                 "is_deleted", "replies", "parent_id")

    def __init__(self, comment_id: int, user_id: int, content: str,
                 created_at: object = None, likes: int = 0,
                 is_deleted: bool = False, parent_id: Optional[int] = None) -> None:
        self.comment_id = comment_id
        self.user_id = user_id
        self.content = content
        self.created_at = created_at
        self.likes = likes
        self.is_deleted = is_deleted
        self.parent_id = parent_id
        self.replies: List["CommentNode"] = []

    def add_reply(self, child: "CommentNode") -> None:
        child.parent_id = self.comment_id
        self.replies.append(child)

    def to_dict(self) -> dict:
        return {
            "comment_id": self.comment_id,
            "user_id": self.user_id,
            "content": "" if self.is_deleted else self.content,
            "is_deleted": self.is_deleted,
            "likes": self.likes,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, "isoformat") else self.created_at,
            "replies": [child.to_dict() for child in self.replies],
        }


# build helpers ----------------------------------------------------------------

def build_thread(rows: Iterable[dict]) -> List[CommentNode]:
    """
    rows: iterable of dicts with keys id, user_id, content, parent_id, likes,
        is_deleted, created_at.

    returns the list of root nodes (no parent). children attach in created_at
    order, mirroring lab 4 ex 1's append based replies list.
    """
    by_id: Dict[int, CommentNode] = {}
    raw = list(rows)
    raw.sort(key=lambda r: r.get("created_at") or 0)
    for row in raw:
        node = CommentNode(
            comment_id=row["id"],
            user_id=row["user_id"],
            content=row.get("content", ""),
            created_at=row.get("created_at"),
            likes=row.get("likes", 0),
            is_deleted=row.get("is_deleted", False),
            parent_id=row.get("parent_id"),
        )
        by_id[node.comment_id] = node
    roots: List[CommentNode] = []
    for node in by_id.values():
        parent = by_id.get(node.parent_id) if node.parent_id else None
        if parent is None:
            roots.append(node)
        else:
            parent.replies.append(node)
    return roots


# recursive helpers (lab 4 ex 1) ----------------------------------------------

def count_total_comments(node: CommentNode) -> int:
    """ref: lab 4 ex 1 count_total_comments. counts deleted nodes too."""
    total = 1
    for reply in node.replies:
        total += count_total_comments(reply)
    return total


def total_likes(node: CommentNode) -> int:
    """ref: lab 4 ex 1 total_likes. deleted comments still aggregate likes."""
    s = node.likes
    for reply in node.replies:
        s += total_likes(reply)
    return s


def find_deepest_reply(node: CommentNode) -> int:
    """ref: lab 4 ex 1 find_deepest_reply. depth of the tallest branch."""
    if not node.replies:
        return 1
    return 1 + max(find_deepest_reply(child) for child in node.replies)


def search_by_user(user_id: int, node: CommentNode) -> List[CommentNode]:
    """ref: lab 4 ex 1 search_by_user. returns every node authored by user_id."""
    out: List[CommentNode] = []
    if node.user_id == user_id and not node.is_deleted:
        out.append(node)
    for reply in node.replies:
        out.extend(search_by_user(user_id, reply))
    return out


def contains_keyword(keyword: str, node: CommentNode) -> bool:
    """ref: lab 4 ex 1 contains_keyword. case insensitive substring match."""
    if not node.is_deleted and keyword.lower() in (node.content or "").lower():
        return True
    for reply in node.replies:
        if contains_keyword(keyword, reply):
            return True
    return False


# pruning (lab 4 ex 1 + ex 2 blend) -------------------------------------------

def prune_deleted(root: Optional[CommentNode]) -> Optional[CommentNode]:
    """
    drop subtrees whose root is deleted AND has no surviving descendants.

    if a deleted node still has surviving children we keep the placeholder so
    the thread shape stays readable in the ui. ref: lab 4 ex 1 delete_comment
    extended with the keep-placeholder rule from claude.md phase 5.
    """
    if root is None:
        return None
    surviving: List[CommentNode] = []
    for reply in root.replies:
        kept = prune_deleted(reply)
        if kept is not None:
            surviving.append(kept)
    root.replies = surviving
    if root.is_deleted and not surviving:
        return None
    return root


def remove_subtree(comment_id: int, root: Optional[CommentNode]) -> Optional[CommentNode]:
    """ref: lab 4 ex 1 delete_comment. cascades by dropping the entire subtree."""
    if root is None:
        return None
    if root.comment_id == comment_id:
        return None
    new_replies: List[CommentNode] = []
    for reply in root.replies:
        kept = remove_subtree(comment_id, reply)
        if kept is not None:
            new_replies.append(kept)
    root.replies = new_replies
    return root


# divide and conquer aggregation (lab 4 ex 2) ---------------------------------

def total_engagement(node: CommentNode,
                     score: Optional[Callable[[CommentNode], float]] = None) -> float:
    """
    bottom up engagement total. ref: lab 4 ex 2 sum_engagement style divide
    and conquer over the comment subtree. score defaults to like count.
    """
    if score is None:
        score = lambda n: float(n.likes)
    own = 0.0 if node.is_deleted else score(node)
    for reply in node.replies:
        own += total_engagement(reply, score)
    return own


# iterative variants (lab 4 ex 3) ---------------------------------------------

def flatten_iterative(root: Optional[CommentNode]) -> List[CommentNode]:
    """
    explicit stack flatten. ref: lab 4 ex 3 flatten_iterative.

    used so deep threads do not blow python's recursion limit. produces nodes
    in the same pre-order sequence as flatten_recursive.
    """
    if root is None:
        return []
    out: List[CommentNode] = []
    stack: List[CommentNode] = [root]
    while stack:
        node = stack.pop()
        out.append(node)
        # push in reverse so the leftmost reply is visited next
        for child in reversed(node.replies):
            stack.append(child)
    return out


def count_iterative(root: Optional[CommentNode]) -> int:
    """ref: lab 4 ex 3 count_comments_loop. iterative twin of count_total_comments."""
    if root is None:
        return 0
    total = 0
    stack: List[CommentNode] = [root]
    while stack:
        node = stack.pop()
        total += 1
        for child in node.replies:
            stack.append(child)
    return total


def thread_summary(root: Optional[CommentNode]) -> dict:
    """convenience wrapper used by the api: depth, count, total likes."""
    if root is None:
        return {"count": 0, "max_depth": 0, "total_likes": 0}
    return {
        "count": count_iterative(root),
        "max_depth": find_deepest_reply(root),
        "total_likes": total_likes(root),
    }


def ensure_recursion_limit(min_limit: int = 5000) -> None:
    """raise the recursion limit if a server is about to recurse into a deep thread."""
    if sys.getrecursionlimit() < min_limit:
        sys.setrecursionlimit(min_limit)
