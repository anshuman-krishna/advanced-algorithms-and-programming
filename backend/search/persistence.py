"""
disk persistence for the lab 1 inverted index and the lab 8 ex 3 tries.

ref: phase 6 follow-up. on cold boot we read a pickle from `backend/.cache/`
and fast path the structures past the full database scan; the disk format is
version tagged so we can change the schema without crashing old workers.

design notes
- we persist plain dictionaries / lists, never the live objects, because
  threading.RLock cannot be pickled.
- the schema VERSION stamp lets us reject stale snapshots after a structural
  change rather than silently mis-loading.
"""

from __future__ import annotations

import os
import pickle
import threading
from pathlib import Path
from typing import List, Tuple

from algorithms.inverted_index import InvertedIndex, get_index
from algorithms.trie import Trie, get_hashtag_trie, get_user_trie


VERSION = 2  # bump when the dict shape changes
CACHE_DIR = Path(os.environ.get("AAP_CACHE_DIR", Path(__file__).resolve().parents[1] / ".cache"))
INDEX_PATH = CACHE_DIR / "inverted_index.pkl"
USER_TRIE_PATH = CACHE_DIR / "user_trie.pkl"
HASHTAG_TRIE_PATH = CACHE_DIR / "hashtag_trie.pkl"

_lock = threading.Lock()


def _ensure_dir() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


# inverted index ---------------------------------------------------------------

def _index_state(idx: InvertedIndex) -> dict:
    return {
        "version": VERSION,
        "posting_lists": {tok: sorted(ids) for tok, ids in idx.posting_lists.items()},
        "document_tokens": {doc: sorted(toks) for doc, toks in idx.document_tokens.items()},
        "term_frequency": idx.term_frequency,
    }


def _index_load(idx: InvertedIndex, state: dict) -> None:
    if state.get("version") != VERSION:
        raise ValueError("inverted index pickle version mismatch")
    idx.reset()
    idx.posting_lists = {tok: set(ids) for tok, ids in state["posting_lists"].items()}
    idx.document_tokens = {doc: set(toks) for doc, toks in state["document_tokens"].items()}
    idx.term_frequency = dict(state.get("term_frequency", {}))
    idx._hydrated = True


# trie -------------------------------------------------------------------------

def _trie_entries(trie: Trie) -> List[Tuple[str, object, float]]:
    """walk the trie collecting (key, payload, weight) for every terminal node."""
    out: List[Tuple[str, object, float]] = []
    stack = [trie.root]
    while stack:
        node = stack.pop()
        if node.is_end:
            out.append((node.key, node.payload, node.weight))
        for child in node.children.values():
            stack.append(child)
    return out


def _trie_state(trie: Trie) -> dict:
    return {"version": VERSION, "entries": _trie_entries(trie)}


def _trie_load(trie: Trie, state: dict) -> None:
    if state.get("version") != VERSION:
        raise ValueError("trie pickle version mismatch")
    trie.hydrate(state["entries"])


# public api -------------------------------------------------------------------

def save_all() -> dict:
    """snapshot every search structure to disk. returns a small report."""
    with _lock:
        _ensure_dir()
        idx = get_index()
        with INDEX_PATH.open("wb") as fh:
            pickle.dump(_index_state(idx), fh)
        with USER_TRIE_PATH.open("wb") as fh:
            pickle.dump(_trie_state(get_user_trie()), fh)
        with HASHTAG_TRIE_PATH.open("wb") as fh:
            pickle.dump(_trie_state(get_hashtag_trie()), fh)
        return {
            "documents": idx.num_documents(),
            "terms": idx.num_terms(),
            "user_trie_path": str(USER_TRIE_PATH),
            "hashtag_trie_path": str(HASHTAG_TRIE_PATH),
            "index_path": str(INDEX_PATH),
        }


def load_all() -> bool:
    """try to load every structure from disk. returns True if all three landed."""
    with _lock:
        if not (INDEX_PATH.exists() and USER_TRIE_PATH.exists() and HASHTAG_TRIE_PATH.exists()):
            return False
        try:
            with INDEX_PATH.open("rb") as fh:
                _index_load(get_index(), pickle.load(fh))
            with USER_TRIE_PATH.open("rb") as fh:
                _trie_load(get_user_trie(), pickle.load(fh))
            with HASHTAG_TRIE_PATH.open("rb") as fh:
                _trie_load(get_hashtag_trie(), pickle.load(fh))
            return True
        except (pickle.PickleError, ValueError, EOFError, OSError):
            return False


def clear_cache() -> None:
    for path in (INDEX_PATH, USER_TRIE_PATH, HASHTAG_TRIE_PATH):
        try:
            path.unlink()
        except FileNotFoundError:
            pass
