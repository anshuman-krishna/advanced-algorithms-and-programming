"""
ref: lab 4 ex 1 recursive comment traversal, lab 4 ex 2 divide and conquer
aggregation, lab 4 ex 3 explicit stack iteration.
"""

import unittest

from algorithms.comment_thread import (
    CommentNode,
    build_thread,
    contains_keyword,
    count_iterative,
    count_total_comments,
    find_deepest_reply,
    flatten_iterative,
    prune_deleted,
    remove_subtree,
    search_by_user,
    thread_summary,
    total_engagement,
    total_likes,
)


def _sample_thread() -> CommentNode:
    root = CommentNode(1, 100, "original post comment", likes=50)
    a = CommentNode(2, 200, "thoughts on recursion?", likes=10)
    b = CommentNode(3, 300, "not sure", likes=5)
    a1 = CommentNode(4, 100, "hopefully not on the exam", likes=20)
    a1a = CommentNode(5, 400, "recursion is hard", likes=100)
    a.add_reply(a1)
    a1.add_reply(a1a)
    root.add_reply(a)
    root.add_reply(b)
    return root


class CommentThreadTests(unittest.TestCase):
    def test_count_total_comments_recursive(self):
        self.assertEqual(count_total_comments(_sample_thread()), 5)

    def test_total_likes_aggregates_subtree(self):
        self.assertEqual(total_likes(_sample_thread()), 50 + 10 + 5 + 20 + 100)

    def test_find_deepest_reply(self):
        # root -> a -> a1 -> a1a
        self.assertEqual(find_deepest_reply(_sample_thread()), 4)

    def test_search_by_user_returns_all_authored(self):
        results = search_by_user(100, _sample_thread())
        ids = sorted(c.comment_id for c in results)
        self.assertEqual(ids, [1, 4])

    def test_contains_keyword_case_insensitive(self):
        self.assertTrue(contains_keyword("recursion", _sample_thread()))
        self.assertTrue(contains_keyword("EXAM", _sample_thread()))
        self.assertFalse(contains_keyword("typescript", _sample_thread()))

    def test_remove_subtree_cascades(self):
        root = _sample_thread()
        remove_subtree(2, root)
        # subtree 2 -> 4 -> 5 should be gone
        ids = [c.comment_id for c in flatten_iterative(root)]
        self.assertEqual(sorted(ids), [1, 3])

    def test_prune_deleted_keeps_placeholder_when_replies_survive(self):
        root = _sample_thread()
        # mark node 2 as deleted; it has children so it must stay as a placeholder
        a = next(c for c in flatten_iterative(root) if c.comment_id == 2)
        a.is_deleted = True
        pruned = prune_deleted(root)
        self.assertIsNotNone(pruned)
        ids = [c.comment_id for c in flatten_iterative(pruned)]
        self.assertIn(2, ids)
        self.assertIn(4, ids)

    def test_prune_deleted_drops_terminal_deleted(self):
        root = _sample_thread()
        # delete a leaf (5). it must vanish entirely
        a1a = next(c for c in flatten_iterative(root) if c.comment_id == 5)
        a1a.is_deleted = True
        pruned = prune_deleted(root)
        ids = [c.comment_id for c in flatten_iterative(pruned)]
        self.assertNotIn(5, ids)
        self.assertIn(4, ids)

    def test_flatten_iterative_matches_pre_order(self):
        root = _sample_thread()
        order = [c.comment_id for c in flatten_iterative(root)]
        self.assertEqual(order, [1, 2, 4, 5, 3])

    def test_count_iterative_matches_recursive(self):
        root = _sample_thread()
        self.assertEqual(count_iterative(root), count_total_comments(root))

    def test_total_engagement_default_likes(self):
        root = _sample_thread()
        self.assertEqual(total_engagement(root), float(total_likes(root)))

    def test_total_engagement_custom_score_skips_deleted(self):
        root = _sample_thread()
        a = next(c for c in flatten_iterative(root) if c.comment_id == 2)
        a.is_deleted = True
        # custom score equally weights every alive node
        score = lambda n: 1.0
        # 5 nodes total, 1 deleted -> 4
        self.assertEqual(total_engagement(root, score), 4.0)

    def test_thread_summary_shape(self):
        s = thread_summary(_sample_thread())
        self.assertEqual(s["count"], 5)
        self.assertEqual(s["max_depth"], 4)
        self.assertEqual(s["total_likes"], 185)

    def test_build_thread_from_rows(self):
        rows = [
            {"id": 1, "user_id": 9, "content": "root", "parent_id": None,
             "likes": 0, "is_deleted": False, "created_at": 1},
            {"id": 2, "user_id": 9, "content": "child", "parent_id": 1,
             "likes": 0, "is_deleted": False, "created_at": 2},
            {"id": 3, "user_id": 9, "content": "grand", "parent_id": 2,
             "likes": 0, "is_deleted": False, "created_at": 3},
            {"id": 4, "user_id": 9, "content": "sibling", "parent_id": 1,
             "likes": 0, "is_deleted": False, "created_at": 4},
        ]
        roots = build_thread(rows)
        self.assertEqual(len(roots), 1)
        self.assertEqual(roots[0].comment_id, 1)
        # children of root must include 2 and 4 in created_at order
        self.assertEqual([c.comment_id for c in roots[0].replies], [2, 4])
        self.assertEqual(roots[0].replies[0].replies[0].comment_id, 3)


if __name__ == "__main__":
    unittest.main()
