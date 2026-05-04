"""
hash table backed inverted index for the post search engine.

ref: claude.md section 5.1 (lab 1: hash tables and fundamentals).
ref: lab 1 exercise 6 (first_unique) for the dict frequency pattern, lab 1
exercise 1 (integer_mirror) for the hash style indexing primitive.

we keep two dictionaries:
    posting_lists: token -> set of doc ids that contain it
    document_tokens: doc id -> set of tokens (cheap removal)

queries are expressed as a tiny boolean grammar built on python set ops:
    - "morning coffee" => intersection (default AND)
    - "morning|coffee" => union (OR)
    - "morning -coffee" => morning AND NOT coffee
"""

from __future__ import annotations

import re
import threading
from typing import Dict, Iterable, List, Optional, Set, Tuple

# alphanumeric plus underscore. lowercase normalized at insert and query time.
_TOKEN_RE = re.compile(r"[a-z0-9_]+")
_HASHTAG_RE = re.compile(r"#([a-z0-9_]+)")


def tokenize(text: str) -> List[str]:
    if not text:
        return []
    lowered = text.lower()
    return _TOKEN_RE.findall(lowered)


def extract_hashtags(text: str) -> List[str]:
    if not text:
        return []
    return _HASHTAG_RE.findall(text.lower())


class InvertedIndex:
    def __init__(self) -> None:
        self.posting_lists: Dict[str, Set[int]] = {}
        self.document_tokens: Dict[int, Set[str]] = {}
        self._lock = threading.RLock()
        self._hydrated = False

    def add_document(self, doc_id: int, text: str) -> None:
        tokens = set(tokenize(text))
        with self._lock:
            self.remove_document(doc_id, _locked=True)
            self.document_tokens[doc_id] = tokens
            for tok in tokens:
                if tok not in self.posting_lists:
                    self.posting_lists[tok] = set()
                self.posting_lists[tok].add(doc_id)

    def remove_document(self, doc_id: int, _locked: bool = False) -> None:
        # caller may already hold the lock during reindex
        ctx = self._noop_lock() if _locked else self._lock
        with ctx:
            tokens = self.document_tokens.pop(doc_id, set())
            for tok in tokens:
                postings = self.posting_lists.get(tok)
                if postings is not None:
                    postings.discard(doc_id)
                    if not postings:
                        self.posting_lists.pop(tok, None)

    def _postings_for(self, token: str) -> Set[int]:
        return self.posting_lists.get(token, set())

    def search(self, query: str) -> List[int]:
        """
        boolean search over the index.

        accepts terms separated by spaces; `term1|term2` evaluates to a union
        of postings. a leading minus excludes documents containing the term.
        """
        if not query:
            return []
        tokens = query.lower().split()
        with self._lock:
            include_terms: List[Set[int]] = []
            exclude_terms: List[Set[int]] = []
            for raw in tokens:
                if not raw:
                    continue
                if raw.startswith("-") and len(raw) > 1:
                    exclude_terms.append(self._postings_for(raw[1:]))
                    continue
                if "|" in raw:
                    accumulator: Set[int] = set()
                    for part in raw.split("|"):
                        if part:
                            accumulator |= self._postings_for(part)
                    include_terms.append(accumulator)
                    continue
                include_terms.append(self._postings_for(raw))

            if include_terms:
                result = set(include_terms[0])
                for s in include_terms[1:]:
                    result &= s
            else:
                # only exclusions, start from the universe of indexed docs
                result = set(self.document_tokens.keys())
            for s in exclude_terms:
                result -= s
            return sorted(result)

    def term_frequency_summary(self) -> Dict[str, int]:
        """ref: lab 1 ex 6 frequency map. how many documents reference each token."""
        with self._lock:
            return {tok: len(docs) for tok, docs in self.posting_lists.items()}

    def num_documents(self) -> int:
        return len(self.document_tokens)

    def num_terms(self) -> int:
        return len(self.posting_lists)

    def hydrate(self, documents: Iterable[Tuple[int, str]]) -> None:
        with self._lock:
            self.posting_lists.clear()
            self.document_tokens.clear()
            for doc_id, text in documents:
                self.add_document(doc_id, text)
            self._hydrated = True

    def is_hydrated(self) -> bool:
        return self._hydrated

    def reset(self) -> None:
        with self._lock:
            self.posting_lists.clear()
            self.document_tokens.clear()
            self._hydrated = False

    def _noop_lock(self):
        # context manager passthrough used when caller already holds the lock
        class _Passthrough:
            def __enter__(self_inner):
                return None

            def __exit__(self_inner, exc_type, exc, tb):
                return False

        return _Passthrough()


_index = InvertedIndex()
_lock = threading.Lock()


def get_index() -> InvertedIndex:
    return _index


def hydrate_from_db() -> InvertedIndex:
    """populate the singleton with caption + hashtag text from posts."""
    from posts.models import Post

    with _lock:
        if _index.is_hydrated():
            return _index
        rows = Post.objects.values_list("id", "caption")
        _index.hydrate(rows)
    return _index


def ensure_hydrated() -> InvertedIndex:
    if not _index.is_hydrated():
        return hydrate_from_db()
    return _index
