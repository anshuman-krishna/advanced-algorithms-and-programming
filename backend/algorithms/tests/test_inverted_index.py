"""
ref: claude.md phase 4 inverted index over hash tables (lab 1).
"""

import unittest

from algorithms.inverted_index import (
    InvertedIndex,
    STOP_WORDS,
    extract_hashtags,
    tokenize,
)


class InvertedIndexTests(unittest.TestCase):
    def setUp(self):
        self.idx = InvertedIndex()
        self.idx.add_document(1, "morning coffee in Lisbon")
        self.idx.add_document(2, "evening run #marathon")
        self.idx.add_document(3, "Coffee with friends in Tokyo")
        self.idx.add_document(4, "long morning run")

    def test_tokenize_lowercases(self):
        self.assertEqual(tokenize("Hello World"), ["hello", "world"])
        self.assertEqual(tokenize("punct? yes!"), ["punct", "yes"])

    def test_extract_hashtags(self):
        self.assertEqual(extract_hashtags("nice #Run today #Marathon"),
                         ["run", "marathon"])

    def test_single_term_search(self):
        self.assertEqual(self.idx.search("coffee"), [1, 3])
        self.assertEqual(self.idx.search("morning"), [1, 4])

    def test_implicit_and(self):
        self.assertEqual(self.idx.search("morning coffee"), [1])

    def test_or_grammar(self):
        self.assertEqual(self.idx.search("coffee|run"), [1, 2, 3, 4])

    def test_negation(self):
        self.assertEqual(self.idx.search("morning -coffee"), [4])

    def test_only_negation(self):
        self.assertEqual(self.idx.search("-coffee"), [2, 4])

    def test_empty_query(self):
        self.assertEqual(self.idx.search(""), [])

    def test_remove_document(self):
        self.idx.remove_document(1)
        self.assertEqual(self.idx.search("coffee"), [3])
        self.assertEqual(self.idx.search("lisbon"), [])

    def test_reindex_replaces_tokens(self):
        self.idx.add_document(1, "rebooted post")
        self.assertEqual(self.idx.search("morning coffee"), [])
        self.assertEqual(self.idx.search("rebooted"), [1])

    def test_term_frequency_summary(self):
        summary = self.idx.term_frequency_summary()
        self.assertEqual(summary["coffee"], 2)
        self.assertEqual(summary["run"], 2)


class InvertedIndexStopWordsTests(unittest.TestCase):
    def test_tokenize_drops_stop_words_by_default(self):
        # "the" and "a" are stop words; "morning" and "coffee" are not
        self.assertEqual(tokenize("the morning of a coffee"), ["morning", "coffee"])

    def test_tokenize_keeps_stop_words_when_asked(self):
        out = tokenize("the morning", drop_stop_words=False)
        self.assertEqual(out, ["the", "morning"])

    def test_stop_word_not_indexed(self):
        idx = InvertedIndex()
        idx.add_document(1, "the morning was good")
        self.assertEqual(idx.search("the"), [])
        self.assertEqual(idx.search("morning"), [1])
        # the stop word should not even be in the posting lists
        self.assertNotIn("the", idx.posting_lists)
        for stop in ("a", "an", "the"):
            self.assertIn(stop, STOP_WORDS)


class InvertedIndexRankedSearchTests(unittest.TestCase):
    def setUp(self):
        self.idx = InvertedIndex()
        # doc 1 mentions coffee 3 times; doc 2 once; doc 3 not at all
        self.idx.add_document(1, "coffee coffee coffee morning")
        self.idx.add_document(2, "morning coffee run")
        self.idx.add_document(3, "evening run marathon")

    def test_ranked_search_orders_by_relevance(self):
        ranked = self.idx.search_ranked("coffee")
        self.assertEqual([pid for pid, _ in ranked], [1, 2])
        # coffee appears more often per token in doc 1, so it must rank first
        self.assertGreater(dict(ranked)[1], dict(ranked)[2])

    def test_ranked_search_multi_term(self):
        ranked = self.idx.search_ranked("coffee run")
        ids = [pid for pid, _ in ranked]
        # doc 2 has both terms; doc 3 has only "run". the doc with both terms
        # must outrank a doc that only contains one of them.
        self.assertIn(2, ids)
        self.assertIn(3, ids)
        self.assertLess(ids.index(2), ids.index(3))

    def test_ranked_search_empty_returns_empty(self):
        self.assertEqual(self.idx.search_ranked(""), [])
        self.assertEqual(self.idx.search_ranked("nothingmatchesthis"), [])

    def test_ranked_search_uses_idf(self):
        # build a corpus where one term is common and another is rare
        idx = InvertedIndex()
        for i in range(5):
            idx.add_document(i, "common")
        idx.add_document(99, "common rare")
        ranked = idx.search_ranked("common rare")
        # the doc with the rare term must rank ahead of the common-only docs
        self.assertEqual(ranked[0][0], 99)


if __name__ == "__main__":
    unittest.main()
