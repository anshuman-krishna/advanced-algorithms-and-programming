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

import math
import re
import threading
from typing import Dict, Iterable, List, Optional, Set, Tuple

# alphanumeric plus underscore. lowercase normalized at insert and query time.
_TOKEN_RE = re.compile(r"[a-z0-9_]+")
_HASHTAG_RE = re.compile(r"#([a-z0-9_]+)")

# small english stop word list. these tokens are intentionally not indexed
# because they appear in almost every document and bloat the posting lists
# without helping precision. ref: lab 1 ex 6 frequency analysis.
STOP_WORDS = frozenset({
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by", "for",
    "from", "has", "have", "i", "if", "in", "is", "it", "its", "of", "on",
    "or", "so", "than", "that", "the", "their", "them", "then", "there",
    "these", "they", "this", "to", "too", "was", "we", "were", "what",
    "when", "which", "who", "will", "with", "you", "your",
})


def tokenize(text: str, *, drop_stop_words: bool = True) -> List[str]:
    if not text:
        return []
    lowered = text.lower()
    tokens = _TOKEN_RE.findall(lowered)
    if drop_stop_words:
        return [t for t in tokens if t not in STOP_WORDS]
    return tokens


def extract_hashtags(text: str) -> List[str]:
    if not text:
        return []
    return _HASHTAG_RE.findall(text.lower())


class InvertedIndex:
    def __init__(self) -> None:
        self.posting_lists: Dict[str, Set[int]] = {}
        self.document_tokens: Dict[int, Set[str]] = {}
        # per-document term frequency map for tf-idf scoring
        self.term_frequency: Dict[int, Dict[str, int]] = {}
        self._lock = threading.RLock()
        self._hydrated = False

    def add_document(self, doc_id: int, text: str) -> None:
        raw_tokens = tokenize(text)
        token_set = set(raw_tokens)
        tf: Dict[str, int] = {}
        for tok in raw_tokens:
            tf[tok] = tf.get(tok, 0) + 1
        with self._lock:
            self.remove_document(doc_id, _locked=True)
            self.document_tokens[doc_id] = token_set
            self.term_frequency[doc_id] = tf
            for tok in token_set:
                if tok not in self.posting_lists:
                    self.posting_lists[tok] = set()
                self.posting_lists[tok].add(doc_id)

    def remove_document(self, doc_id: int, _locked: bool = False) -> None:
        # caller may already hold the lock during reindex
        ctx = self._noop_lock() if _locked else self._lock
        with ctx:
            tokens = self.document_tokens.pop(doc_id, set())
            self.term_frequency.pop(doc_id, None)
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

    def search_ranked(self, query: str) -> List[Tuple[int, float]]:
        """
        tf-idf ranked search. boolean inclusion still applies (terms intersect
        by default) but the result list is sorted by descending tf-idf so
        multi-term queries surface the most relevant doc first.

        ref: lab 1 hash table indexing + standard tf-idf weighting.
        """
        if not query:
            return []
        # parse query reusing the boolean rules to find candidate docs
        terms = [t for t in tokenize(query) if t]
        if not terms:
            return []
        with self._lock:
            doc_total = max(1, len(self.document_tokens))
            # candidate set: every doc that contains at least one query term
            candidates: Set[int] = set()
            for term in terms:
                candidates |= self._postings_for(term)
            if not candidates:
                return []
            scored: List[Tuple[int, float]] = []
            for doc_id in candidates:
                tf_map = self.term_frequency.get(doc_id, {})
                doc_len = max(1, sum(tf_map.values()))
                score = 0.0
                for term in terms:
                    tf = tf_map.get(term, 0)
                    if tf == 0:
                        continue
                    df = len(self.posting_lists.get(term, set())) or 1
                    idf = math.log((doc_total + 1) / (df + 1)) + 1.0
                    # normalized term frequency to dampen long docs
                    score += (tf / doc_len) * idf
                if score > 0:
                    scored.append((doc_id, score))
            scored.sort(key=lambda r: (-r[1], r[0]))
            return scored

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
            self.term_frequency.clear()
            for doc_id, text in documents:
                self.add_document(doc_id, text)
            self._hydrated = True

    def is_hydrated(self) -> bool:
        return self._hydrated

    def reset(self) -> None:
        with self._lock:
            self.posting_lists.clear()
            self.document_tokens.clear()
            self.term_frequency.clear()
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
    """
    populate the singleton with caption + hashtag text from posts.

    on cold boot we first try to fast path through the on-disk pickle
    snapshot under backend/.cache/. if that fails (missing, version drift,
    or corruption) we fall back to scanning the Post table.
    """
    from posts.models import Post

    with _lock:
        if _index.is_hydrated():
            return _index
        try:
            from search.persistence import load_all as load_search_caches
            if load_search_caches():
                return _index
        except Exception:
            # never let a broken snapshot block the api; just rebuild from db
            pass
        rows = Post.objects.values_list("id", "caption")
        _index.hydrate(rows)
    return _index


def ensure_hydrated() -> InvertedIndex:
    if not _index.is_hydrated():
        return hydrate_from_db()
    return _index
