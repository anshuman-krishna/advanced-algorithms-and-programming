"""
ref: lab 8 ex 3 prefix trie autocomplete.
"""

import unittest

from algorithms.trie import Trie


class TrieTests(unittest.TestCase):
    def setUp(self):
        self.t = Trie()
        self.t.insert("alice", payload=1, weight=5.0)
        self.t.insert("alec", payload=2, weight=8.0)
        self.t.insert("alex", payload=3, weight=2.0)
        self.t.insert("bob", payload=4, weight=4.0)

    def test_search_exact(self):
        self.assertEqual(self.t.search("alice"), 1)
        self.assertIsNone(self.t.search("ali"))
        self.assertIsNone(self.t.search("missing"))

    def test_starts_with(self):
        self.assertTrue(self.t.starts_with("al"))
        self.assertFalse(self.t.starts_with("zz"))

    def test_autocomplete_orders_by_weight(self):
        results = self.t.autocomplete("al", max_results=3)
        keys = [k for k, _, _ in results]
        self.assertEqual(keys, ["alec", "alice", "alex"])

    def test_autocomplete_respects_limit(self):
        results = self.t.autocomplete("a", max_results=2)
        self.assertEqual(len(results), 2)

    def test_autocomplete_unknown_prefix(self):
        self.assertEqual(self.t.autocomplete("zz"), [])

    def test_increment_weight_promotes(self):
        self.t.increment_weight("alex", delta=20.0)
        results = self.t.autocomplete("al", max_results=3)
        self.assertEqual(results[0][0], "alex")

    def test_delete(self):
        self.t.delete("alice")
        self.assertIsNone(self.t.search("alice"))
        # alec stays because it shares the "al" prefix
        self.assertEqual(self.t.search("alec"), 2)


if __name__ == "__main__":
    unittest.main()
