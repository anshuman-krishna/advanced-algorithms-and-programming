"""
sqlite spillover for the in-memory NotificationQueue so a process restart
does not drop pending events.

ref: phase 5 follow-up. lab 3 ex 2 NotificationQueue. on AppConfig.ready we
load every still-pending row back onto the deque, then delete those rows.
on every enqueue we also append a row so the spillover survives a crash. the
drainer purges the spillover row alongside the in-memory pop.

design notes
- spillover lives at backend/.cache/notifications_queue.sqlite3, not the main
  django db, so test runs and ops scripts never collide with production data.
- the table is intentionally tiny: id, payload (json), is_priority. no
  schema migrations because this is a side-channel buffer, not a system of
  record. the persisted Notification row produced after drain is the truth.
"""

from __future__ import annotations

import json
import os
import sqlite3
import threading
from pathlib import Path
from typing import List, Optional

CACHE_DIR = Path(os.environ.get("AAP_CACHE_DIR", Path(__file__).resolve().parents[1] / ".cache"))
PATH = CACHE_DIR / "notifications_queue.sqlite3"

_lock = threading.Lock()
_initialized = False


def _ensure_dir() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _connect() -> sqlite3.Connection:
    _ensure_dir()
    conn = sqlite3.connect(str(PATH))
    conn.execute(
        "CREATE TABLE IF NOT EXISTS spillover ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "payload TEXT NOT NULL, "
        "is_priority INTEGER NOT NULL DEFAULT 0)"
    )
    return conn


def append(payload: dict) -> Optional[int]:
    """write a single event row. returns the spillover id or None on failure."""
    with _lock:
        try:
            conn = _connect()
            try:
                cur = conn.execute(
                    "INSERT INTO spillover (payload, is_priority) VALUES (?, ?)",
                    (json.dumps(payload), 1 if payload.get("is_priority") else 0),
                )
                conn.commit()
                return cur.lastrowid
            finally:
                conn.close()
        except sqlite3.Error:
            return None


def remove(spillover_id: int) -> None:
    if spillover_id is None:
        return
    with _lock:
        try:
            conn = _connect()
            try:
                conn.execute("DELETE FROM spillover WHERE id = ?", (spillover_id,))
                conn.commit()
            finally:
                conn.close()
        except sqlite3.Error:
            return


def drain_all() -> List[dict]:
    """read every spillover row in insertion order and clear the table."""
    global _initialized
    with _lock:
        try:
            conn = _connect()
            try:
                rows = conn.execute(
                    "SELECT id, payload FROM spillover ORDER BY id ASC"
                ).fetchall()
                conn.execute("DELETE FROM spillover")
                conn.commit()
            finally:
                conn.close()
        except sqlite3.Error:
            return []
        _initialized = True
        out: List[dict] = []
        for _, raw in rows:
            try:
                out.append(json.loads(raw))
            except json.JSONDecodeError:
                continue
        return out


def already_initialized() -> bool:
    return _initialized
