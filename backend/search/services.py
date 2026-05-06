"""
phase 4 service layer composing the inverted index, tries, recommender, and
generalized category tree.

views in this app should call into this module rather than touching the
algorithm helpers directly.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum

from algorithms import (
    category_tree as cat,
    inverted_index,
    recommender,
    trie as trie_module,
)
from algorithms.scoring import score_batch

User = get_user_model()


# inverted index passthroughs
def search_posts(query: str) -> List[int]:
    return inverted_index.ensure_hydrated().search(query)


def search_posts_ranked(query: str) -> List[Tuple[int, float]]:
    """ref: lab 1 hash table indexing + tf-idf ranking."""
    return inverted_index.ensure_hydrated().search_ranked(query)


def index_post(post_id: int, text: str) -> None:
    inverted_index.get_index().add_document(post_id, text)


def deindex_post(post_id: int) -> None:
    inverted_index.get_index().remove_document(post_id)


def index_stats() -> Dict[str, int]:
    idx = inverted_index.ensure_hydrated()
    return {"documents": idx.num_documents(), "terms": idx.num_terms()}


# trie passthroughs
def autocomplete_users(prefix: str, limit: int = 10) -> List[Tuple[str, int, float]]:
    return [
        (key, payload, weight)
        for key, payload, weight in trie_module.ensure_user_trie().autocomplete(prefix.lower(), limit)
    ]


def autocomplete_hashtags(prefix: str, limit: int = 10) -> List[Tuple[str, int, float]]:
    return [
        (key, payload, weight)
        for key, payload, weight in trie_module.ensure_hashtag_trie().autocomplete(prefix.lower().lstrip("#"), limit)
    ]


# category tree
def build_category_tree(post_assignments: Optional[Dict[int, Set[int]]] = None,
                        engagement_lookup: Optional[Dict[int, float]] = None) -> Optional[cat.CategoryNode]:
    """
    construct an in memory generalized tree from the Category table.

    optional `post_assignments` maps category_id to a set of post_ids.
    optional `engagement_lookup` maps post_id to engagement score.
    """
    from .models import Category, PostCategory

    rows = list(Category.objects.values("id", "name", "parent_id"))
    root = cat.build_from_rows(rows)
    if root is None:
        return None
    if post_assignments is None:
        post_assignments = {}
        for category_id, post_id in PostCategory.objects.values_list("category_id", "post_id"):
            post_assignments.setdefault(category_id, set()).add(post_id)
    _attach_post_ids(root, post_assignments)
    if engagement_lookup is None:
        engagement_lookup = _engagement_lookup_for(root)
    cat.post_order_aggregate(root, engagement_lookup)
    return root


def _attach_post_ids(node: cat.CategoryNode,
                     assignments: Dict[int, Set[int]]) -> None:
    node.post_ids = set(assignments.get(node.category_id, set()))
    for child in node.children:
        _attach_post_ids(child, assignments)


def _engagement_lookup_for(root: cat.CategoryNode) -> Dict[int, float]:
    """build engagement = like count per post for posts in the subtree."""
    from posts.models import Post

    post_ids = list(cat.collect_subtree_post_ids(root))
    if not post_ids:
        return {}
    rows = (
        Post.objects.filter(id__in=post_ids)
        .annotate(annotated_likes=Count("likes"))
        .values("id", "annotated_likes", "created_at")
    )
    triples = [(r["id"], r["annotated_likes"], r["created_at"]) for r in rows]
    return dict(score_batch(triples))


def category_engagement(category_id: int) -> dict:
    """surface bottom up engagement for a single category subtree."""
    root = build_category_tree()
    if root is None:
        return {}
    target = cat.find(root, category_id)
    if target is None:
        return {}
    return cat.serialize(target)


def explore_tree() -> dict:
    """full explore taxonomy with aggregated engagement per node."""
    root = build_category_tree()
    if root is None:
        return {}
    return cat.serialize(root)


# recommender
def _user_likes_map() -> Dict[int, Set[int]]:
    from posts.models import Like

    out: Dict[int, Set[int]] = {}
    for user_id, post_id in Like.objects.values_list("user_id", "post_id"):
        out.setdefault(user_id, set()).add(post_id)
    return out


def _post_likes_map() -> Dict[int, Set[int]]:
    from posts.models import Like

    out: Dict[int, Set[int]] = {}
    for user_id, post_id in Like.objects.values_list("user_id", "post_id"):
        out.setdefault(post_id, set()).add(user_id)
    return out


def recommend_posts(user_id: int, strategy: str = "jaccard",
                    max_results: int = 10) -> List[Tuple[int, float]]:
    user_likes = _user_likes_map()
    if strategy == "cosine":
        post_likes = _post_likes_map()
        return recommender.recommend_by_cosine(user_id, user_likes, post_likes,
                                               max_results=max_results)
    return recommender.recommend_by_jaccard(user_id, user_likes,
                                            max_results=max_results)
