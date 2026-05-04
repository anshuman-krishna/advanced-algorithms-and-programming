"""
ref: claude.md phase 4 inverted index over hash tables (lab 1).
"""

import unittest

from algorithms.inverted_index import InvertedIndex, extract_hashtags, tokenize


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


if __name__ == "__main__":
    unittest.main()
