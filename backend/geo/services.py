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


EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """great circle distance in kilometres. accurate at any latitude."""
    import math

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = (
        math.sin(dphi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return EARTH_RADIUS_KM * c


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
           limit: int = 50, *, unit: str = "deg") -> List[dict]:
    """
    ref: lab 7 ex 1 radius variant.

    when unit='deg' the radius is treated as planar degrees (the quadtree
    indexes lat/lng directly). when unit='km' we convert the requested radius
    into a degree bounding box that always overestimates, then filter the
    candidates by haversine_km so users near the poles see the same effective
    radius as users near the equator.
    """
    hydrate_if_empty()
    if unit == "km":
        # at the equator, 1 deg ~= 111 km. we use a generous overestimate to
        # ensure the bounding box never misses true neighbours at high latitudes
        # then filter the candidates with haversine.
        deg_estimate = max(0.001, (radius_deg / 111.0) * 1.5)
        candidates = _tree.radius_query(lng, lat, deg_estimate)
        out = []
        for h in candidates:
            km = haversine_km(lat, lng, h["y"], h["x"])
            if km <= radius_deg:
                h = {**h, "distance_km": km}
                out.append(h)
        out.sort(key=lambda h: h["distance_km"])
        return out[:limit]
    hits = _tree.radius_query(lng, lat, radius_deg)
    for h in hits:
        h["distance_km"] = haversine_km(lat, lng, h["y"], h["x"])
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


def dense_regions(threshold: int = 1, min_size: float = 1.0) -> list:
    """ref: lab 7 ex 1 find_dense_regions. delegates to the underlying quadtree."""
    hydrate_if_empty()
    return _tree.dense_regions(threshold=threshold, min_size=min_size)


def stats() -> dict:
    return {"size": _tree.size, "hydrated": _hydrated}


def force_reset() -> None:
    global _hydrated
    with _lock:
        _tree.hydrate([])
        _hydrated = False
