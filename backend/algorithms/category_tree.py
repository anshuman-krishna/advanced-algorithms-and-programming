"""
generalized tree for the explore category taxonomy.

ref: lab 5 exercise 3 (generalized_trees_and_representation) for the GeneralizedNode
shape and traversals.
ref: lab 5 exercise 2 (tree_traversals_for_content_processing) for the bottom up
post_order_total_posts engagement aggregator.

a category like "tech" can carry children "ai", "hardware", "software" and so on.
each leaf maps to a flat list of post ids; engagement aggregates upward via
post order traversal so the parent reflects the union of its subtree.
"""

from __future__ import annotations

from collections import deque
from typing import Dict, Iterable, List, Optional, Set


class CategoryNode:
    __slots__ = ("category_id", "name", "post_ids", "children", "parent",
                 "total_engagement", "total_posts")

    def __init__(self, category_id: int, name: str,
                 post_ids: Optional[Iterable[int]] = None) -> None:
        self.category_id = category_id
        self.name = name
        self.post_ids: Set[int] = set(post_ids or [])
        self.children: List["CategoryNode"] = []
        self.parent: Optional["CategoryNode"] = None
        # filled by post_order_aggregate
        self.total_engagement: float = 0.0
        self.total_posts: int = 0

    def add_child(self, child: "CategoryNode") -> None:
        child.parent = self
        self.children.append(child)


def pre_order_names(root: Optional[CategoryNode]) -> List[str]:
    out: List[str] = []
    if root is None:
        return out
    out.append(root.name)
    for child in root.children:
        out.extend(pre_order_names(child))
    return out


def level_order(root: Optional[CategoryNode]) -> List[str]:
    out: List[str] = []
    if root is None:
        return out
    queue = deque([root])
    while queue:
        node = queue.popleft()
        out.append(node.name)
        for child in node.children:
            queue.append(child)
    return out


def height(root: Optional[CategoryNode]) -> int:
    if root is None:
        return 0
    if not root.children:
        return 1
    return 1 + max(height(child) for child in root.children)


def count_nodes(root: Optional[CategoryNode]) -> int:
    if root is None:
        return 0
    total = 1
    for child in root.children:
        total += count_nodes(child)
    return total


def post_order_aggregate(root: Optional[CategoryNode],
                         engagement_lookup: Dict[int, float]) -> float:
    """
    bottom up engagement total. ref: lab 5 ex 2 post_order_total_posts.

    each node accumulates its own posts plus every child subtree, and writes
    the total back to the node so it can be served without recomputing.
    """
    if root is None:
        return 0.0
    own = sum(engagement_lookup.get(post_id, 0.0) for post_id in root.post_ids)
    own_posts = len(root.post_ids)
    for child in root.children:
        own += post_order_aggregate(child, engagement_lookup)
        own_posts += child.total_posts
    root.total_engagement = own
    root.total_posts = own_posts
    return own


def find(root: Optional[CategoryNode], category_id: int) -> Optional[CategoryNode]:
    if root is None:
        return None
    if root.category_id == category_id:
        return root
    for child in root.children:
        hit = find(child, category_id)
        if hit is not None:
            return hit
    return None


def collect_subtree_post_ids(root: Optional[CategoryNode]) -> Set[int]:
    """union of all post ids in the subtree rooted at `root`."""
    if root is None:
        return set()
    out = set(root.post_ids)
    for child in root.children:
        out |= collect_subtree_post_ids(child)
    return out


def serialize(root: Optional[CategoryNode]) -> dict:
    if root is None:
        return {}
    return {
        "category_id": root.category_id,
        "name": root.name,
        "post_count": len(root.post_ids),
        "total_posts": root.total_posts,
        "total_engagement": root.total_engagement,
        "children": [serialize(child) for child in root.children],
    }


def build_from_rows(rows: Iterable[dict]) -> Optional[CategoryNode]:
    """
    rows: iterable of {id, name, parent_id} dicts. returns the root.

    supports a single root forest by attaching orphans under a synthetic root
    when more than one row has parent_id None.
    """
    nodes: Dict[int, CategoryNode] = {}
    raw = list(rows)
    for row in raw:
        nodes[row["id"]] = CategoryNode(row["id"], row["name"])
    roots: List[CategoryNode] = []
    for row in raw:
        node = nodes[row["id"]]
        parent_id = row.get("parent_id")
        if parent_id is None:
            roots.append(node)
        else:
            parent = nodes.get(parent_id)
            if parent is not None:
                parent.add_child(node)
            else:
                roots.append(node)
    if not roots:
        return None
    if len(roots) == 1:
        return roots[0]
    synthetic = CategoryNode(-1, "explore")
    for r in roots:
        synthetic.add_child(r)
    return synthetic
