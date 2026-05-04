"""
ref: claude.md phase 3 weighted formula `(0.7 * likes) + (0.3 * recency)`.
"""

import unittest
from datetime import datetime, timedelta, timezone

from algorithms.scoring import (
    LIKES_WEIGHT,
    RECENCY_WEIGHT,
    normalize_likes,
    recency_factor,
    score_batch,
    score_post,
)


class ScoringTests(unittest.TestCase):
    def test_weights_sum_to_one(self):
        self.assertAlmostEqual(LIKES_WEIGHT + RECENCY_WEIGHT, 1.0)

    def test_normalize_likes_bounds(self):
        self.assertEqual(normalize_likes(0, 100), 0.0)
        self.assertEqual(normalize_likes(100, 100), 1.0)
        self.assertGreater(normalize_likes(50, 100), 0.0)
        self.assertLess(normalize_likes(50, 100), 1.0)

    def test_normalize_likes_zero_max(self):
        self.assertEqual(normalize_likes(10, 0), 0.0)

    def test_recency_factor_clamps(self):
        now = datetime(2026, 5, 4, 12, 0, tzinfo=timezone.utc)
        fresh = now - timedelta(minutes=5)
        stale = now - timedelta(hours=48)
        self.assertAlmostEqual(recency_factor(fresh, now=now), 1 - (5 / 60) / 24, places=4)
        self.assertEqual(recency_factor(stale, now=now), 0.0)

    def test_recency_factor_naive_datetime(self):
        now = datetime(2026, 5, 4, 12, 0, tzinfo=timezone.utc)
        naive = datetime(2026, 5, 4, 11, 0)
        self.assertGreater(recency_factor(naive, now=now), 0.9)

    def test_score_post_blend(self):
        now = datetime(2026, 5, 4, 12, 0, tzinfo=timezone.utc)
        created = now - timedelta(hours=12)
        # likes 50/100 -> normalized via log scale, recency at half window = 0.5
        s = score_post(50, created, max_likes=100, now=now)
        self.assertGreater(s, 0.0)
        self.assertLess(s, 1.0)

    def test_score_batch_orders_by_score(self):
        now = datetime(2026, 5, 4, 12, 0, tzinfo=timezone.utc)
        triples = [
            (1, 1, now - timedelta(hours=20)),
            (2, 100, now - timedelta(minutes=1)),
            (3, 50, now - timedelta(hours=23, minutes=59)),
        ]
        scored = dict(score_batch(triples, now=now))
        self.assertGreater(scored[2], scored[1])
        self.assertGreater(scored[2], scored[3])

    def test_score_batch_empty(self):
        self.assertEqual(score_batch([]), [])


if __name__ == "__main__":
    unittest.main()
