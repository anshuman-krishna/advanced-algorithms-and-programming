"""
ref: lab 2 ex 2 and ex 4 verifications.
"""

import unittest

from algorithms.sets_ops import (
    cosine_similarity,
    difference,
    intersection,
    jaccard_similarity,
    mutual_followers,
    mutual_pairs,
    suggest_friends_by_set_difference,
    union,
)


class SetOpsTests(unittest.TestCase):
    def test_intersection_difference_union(self):
        a = {1, 2, 3}
        b = {2, 3, 4}
        self.assertEqual(intersection(a, b), {2, 3})
        self.assertEqual(difference(a, b), {1})
        self.assertEqual(union(a, b), {1, 2, 3, 4})

    def test_jaccard_known_values(self):
        self.assertEqual(jaccard_similarity({1, 2}, {1, 2}), 1.0)
        self.assertEqual(jaccard_similarity(set(), set()), 0.0)
        self.assertAlmostEqual(jaccard_similarity({1, 2}, {2, 3}), 1 / 3)

    def test_cosine_similarity(self):
        self.assertEqual(cosine_similarity([0, 0], [1, 1]), 0.0)
        self.assertAlmostEqual(cosine_similarity([1, 0], [1, 0]), 1.0)
        self.assertAlmostEqual(cosine_similarity([1, 0], [0, 1]), 0.0)

    def test_mutual_followers(self):
        followers_of_a = {10, 20, 30}
        followers_of_b = {20, 30, 40}
        self.assertEqual(mutual_followers(followers_of_a, followers_of_b), {20, 30})

    def test_mutual_pairs_dedup(self):
        following_map = {1: {2}, 2: {1, 3}, 3: {2}}
        pairs = mutual_pairs(following_map)
        self.assertIn((1, 2), pairs)
        self.assertIn((2, 3), pairs)
        self.assertEqual(len(pairs), 2)

    def test_mutual_pairs_skip_self(self):
        # user 4 lists itself, should be ignored
        pairs = mutual_pairs({4: {4}})
        self.assertEqual(pairs, [])

    def test_suggest_friends_by_set_difference(self):
        following_map = {1: {2, 3}, 2: {1, 4, 5}, 3: {1, 5, 6}}
        suggestions = suggest_friends_by_set_difference(1, following_map[1], following_map)
        self.assertEqual(suggestions, {4, 5, 6})


if __name__ == "__main__":
    unittest.main()
