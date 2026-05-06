"""
disk persistence for per-user DailySegmentTree state.

ref: phase 6 follow-up. lab 8 ex 3 segment tree. we persist the daily series
plus the origin date and window so a restart doesn't have to replay every
Like row to rebuild the structure.
"""

from __future__ import annotations

import os
import pickle
import threading
from datetime import date
from pathlib import Path
from typing import Dict

from algorithms.segment_tree import DailySegmentTree


VERSION = 1
CACHE_DIR = Path(os.environ.get("AAP_CACHE_DIR", Path(__file__).resolve().parents[1] / ".cache"))
PATH = CACHE_DIR / "analytics_segment_trees.pkl"

_lock = threading.Lock()


def _ensure_dir() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def save(trees: Dict[int, DailySegmentTree]) -> dict:
    with _lock:
        _ensure_dir()
        snapshot = {
            "version": VERSION,
            "trees": {
                user_id: {
                    "origin": tree.origin.isoformat(),
                    "window_days": tree.window_days,
                    "series": list(tree.daily_series()),
                }
                for user_id, tree in trees.items()
            },
        }
        with PATH.open("wb") as fh:
            pickle.dump(snapshot, fh)
        return {"users": len(snapshot["trees"]), "path": str(PATH)}


def load() -> Dict[int, DailySegmentTree]:
    if not PATH.exists():
        return {}
    with _lock:
        try:
            with PATH.open("rb") as fh:
                payload = pickle.load(fh)
        except (pickle.PickleError, EOFError, OSError):
            return {}
    if payload.get("version") != VERSION:
        return {}
    out: Dict[int, DailySegmentTree] = {}
    for user_id, snap in payload["trees"].items():
        origin = date.fromisoformat(snap["origin"])
        tree = DailySegmentTree(origin, window_days=snap["window_days"])
        for offset, value in enumerate(snap["series"]):
            if value:
                tree.set(origin.fromordinal(origin.toordinal() + offset), value)
        out[int(user_id)] = tree
    return out


def clear_cache() -> None:
    try:
        PATH.unlink()
    except FileNotFoundError:
        pass
