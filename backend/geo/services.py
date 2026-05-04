"""
geo service over the quadtree primitive.

ref: claude.md section 5.7 (lab 7 spatial algorithms).
ref: lab 7 ex 1 divide and conquer spatial splitting. we keep one process-wide
quadtree covering the entire planet (longitude in [-180, 180], latitude in
[-90, 90]) and let the Post signals push / pop entries.

design notes
- coordinate convention: x = longitude, y = latitude. callers always pass
  (lat, lng) at the api boundary; this module flips the order internally so
  the underlying quadtree is unaware of the geo semantics.
- only posts with non-null latitude AND longitude land in the tree. all other
  posts are simply absent.
- range_query / radius_query return the post payload (id, caption, author,
  created_at) so the frontend can render results without a follow-up fetch.
"""

from __future__ import annotations

import threading
from typing import Any, List, Optional, Tuple

from algorithms.quadtree import BoundingBox, QuadTree


_lock = threading.Lock()
_hydrated = False
_tree = QuadTree(BoundingBox(-180.0, -90.0, 180.0, 90.0))


def _payload_from_post(post) -> dict:
    return {
        "post_id": post.id,
        "author_id": post.author_id,
        "author_username": getattr(post.author, "username", ""),
        "caption": post.caption,
        "location": post.location,
        "created_at": post.created_at.isoformat() if post.created_at else None,
    }


def hydrate_from_db() -> int:
    """rebuild the quadtree from every post that carries coordinates."""
    from posts.models import Post

    qs = (
        Post.objects
        .select_related("author")
        .filter(latitude__isnull=False, longitude__isnull=False)
    )
    items: List[Tuple[float, float, Any, Optional[dict]]] = []
    for p in qs:
        items.append((float(p.longitude), float(p.latitude), p.id, _payload_from_post(p)))
    _tree.hydrate(items)
    return _tree.size


def hydrate_if_empty() -> int:
    global _hydrated
    if _hydrated:
        return _tree.size
    with _lock:
        if _hydrated:
            return _tree.size
        size = hydrate_from_db()
        _hydrated = True
        return size


def upsert_post(post) -> bool:
    """signal entry point. returns True if the post was actually placed."""
    if post.latitude is None or post.longitude is None:
        # if a post lost its coords, drop it from the tree
        return _tree.remove(post.id)
    hydrate_if_empty()
    _tree.remove(post.id)
    return _tree.insert(
        float(post.longitude), float(post.latitude), post.id, _payload_from_post(post),
    )


def remove_post(post_id: int) -> bool:
    return _tree.remove(post_id)


def nearby(lat: float, lng: float, radius_deg: float = 1.0,
           limit: int = 50) -> List[dict]:
    """ref: lab 7 ex 1 radius variant. radius is in degrees, planar approximation."""
    hydrate_if_empty()
    hits = _tree.radius_query(lng, lat, radius_deg)
    # sort by distance from query point so the closest sits first
    hits.sort(key=lambda h: (h["x"] - lng) ** 2 + (h["y"] - lat) ** 2)
    return hits[:limit]


def bbox(min_lat: float, min_lng: float, max_lat: float, max_lng: float,
         limit: int = 200) -> List[dict]:
    """ref: lab 7 ex 1 count_points_in_region, returning the points themselves."""
    hydrate_if_empty()
    rect = BoundingBox(min_lng, min_lat, max_lng, max_lat)
    hits = _tree.range_query(rect)
    return hits[:limit]


def nearest(lat: float, lng: float, k: int = 5) -> List[dict]:
    """ref: lab 7 ex 1 traversal extended to k nearest."""
    hydrate_if_empty()
    return _tree.nearest(lng, lat, k=k)


def stats() -> dict:
    return {"size": _tree.size, "hydrated": _hydrated}


def force_reset() -> None:
    global _hydrated
    with _lock:
        _tree.hydrate([])
        _hydrated = False
