"""
ref: lab 2 ex 2 jaccard, lab 2 ex 3 cosine.
"""

import unittest

from algorithms.recommender import (
    cosine_post_similarity,
    jaccard_user_similarity,
    recommend_by_cosine,
    recommend_by_jaccard,
)


class RecommenderTests(unittest.TestCase):
    def test_jaccard_user_similarity(self):
        self.assertAlmostEqual(jaccard_user_similarity({1, 2}, {2, 3}), 1 / 3)
        self.assertEqual(jaccard_user_similarity(set(), set()), 0.0)

    def test_recommend_by_jaccard_excludes_already_liked(self):
        user_likes = {
            10: {1, 2, 3},
            20: {2, 3, 4},
            30: {3, 4, 5},
            40: {6, 7},
        }
        ranked = recommend_by_jaccard(10, user_likes)
        ids = {pid for pid, _ in ranked}
        self.assertNotIn(1, ids)
        self.assertNotIn(2, ids)
        self.assertIn(4, ids)
        # user 20 has higher overlap with target than user 30, so post 4 should rank above post 5
        ordered = [pid for pid, _ in ranked]
        self.assertLess(ordered.index(4), ordered.index(5))

    def test_recommend_by_jaccard_empty_target(self):
        self.assertEqual(recommend_by_jaccard(99, {}), [])

    def test_cosine_post_similarity(self):
        self.assertAlmostEqual(
            cosine_post_similarity({1, 2}, {1, 2}), 1.0
        )
        self.assertEqual(cosine_post_similarity(set(), {1}), 0.0)

    def test_recommend_by_cosine(self):
        user_likes = {
            10: {1, 2},
            20: {2, 3},
            30: {1, 3, 4},
        }
        post_likes = {
            1: {10, 30},
            2: {10, 20},
            3: {20, 30},
            4: {30},
        }
        ranked = recommend_by_cosine(10, user_likes, post_likes)
        ids = [pid for pid, _ in ranked]
        self.assertIn(3, ids)
        self.assertIn(4, ids)
        # post 1 and 2 are already liked, must not recommend
        self.assertNotIn(1, ids)
        self.assertNotIn(2, ids)


if __name__ == "__main__":
    unittest.main()
