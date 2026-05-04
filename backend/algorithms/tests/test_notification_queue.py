"""
ref: lab 3 ex 2 NotificationQueue enqueue, dequeue, priority_enqueue, batch_process.
"""

import unittest

from algorithms.notification_queue import NotificationQueue


class NotificationQueueTests(unittest.TestCase):
    def setUp(self):
        self.q = NotificationQueue()

    def test_fifo_order(self):
        for i in range(3):
            self.q.enqueue({"id": i})
        self.assertEqual(self.q.dequeue(), {"id": 0})
        self.assertEqual(self.q.dequeue(), {"id": 1})
        self.assertEqual(self.q.dequeue(), {"id": 2})

    def test_dequeue_empty_returns_none(self):
        self.assertIsNone(self.q.dequeue())

    def test_priority_enqueue_jumps_front(self):
        self.q.enqueue({"id": 1})
        self.q.enqueue({"id": 2})
        self.q.priority_enqueue({"id": 99, "kind": "urgent"})
        self.assertEqual(self.q.dequeue(), {"id": 99, "kind": "urgent"})
        self.assertEqual(self.q.dequeue(), {"id": 1})

    def test_batch_process_drains_at_most_k(self):
        for i in range(5):
            self.q.enqueue({"id": i})
        drained = self.q.batch_process(3)
        self.assertEqual([d["id"] for d in drained], [0, 1, 2])
        self.assertEqual(len(self.q), 2)

    def test_batch_process_handler_invoked(self):
        seen = []
        for i in range(2):
            self.q.enqueue({"id": i})
        self.q.batch_process(10, handler=lambda x: seen.append(x["id"]))
        self.assertEqual(seen, [0, 1])

    def test_processed_log_records_drained(self):
        for i in range(3):
            self.q.enqueue({"id": i})
        self.q.batch_process(2)
        self.assertEqual([p["id"] for p in self.q.processed()], [0, 1])

    def test_peek_does_not_pop(self):
        self.q.enqueue({"id": 7})
        self.assertEqual(self.q.peek(), {"id": 7})
        self.assertEqual(len(self.q), 1)

    def test_stats_shape(self):
        self.q.enqueue({"id": 1})
        self.q.enqueue({"id": 2})
        self.q.batch_process(1)
        stats = self.q.stats()
        self.assertEqual(stats, {"pending": 1, "processed": 1})

    def test_clear_resets(self):
        self.q.enqueue({"id": 1})
        self.q.batch_process(1)
        self.q.clear()
        self.assertEqual(self.q.stats(), {"pending": 0, "processed": 0})


class NotificationQueueConcurrencyTests(unittest.TestCase):
    def test_concurrent_enqueue_preserves_count(self):
        import threading

        q = NotificationQueue()

        def worker():
            for _ in range(200):
                q.enqueue({"x": 1})

        threads = [threading.Thread(target=worker) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(len(q), 800)

    def test_priority_then_normal_order(self):
        q = NotificationQueue()
        q.enqueue({"id": 1})
        q.enqueue({"id": 2})
        q.priority_enqueue({"id": "p1"})
        q.priority_enqueue({"id": "p2"})
        # priority is a stack onto the front: p2 then p1 then 1 then 2
        ids = []
        while True:
            item = q.dequeue()
            if item is None:
                break
            ids.append(item["id"])
        self.assertEqual(ids, ["p2", "p1", 1, 2])

    def test_batch_process_with_k_zero_is_noop(self):
        q = NotificationQueue()
        q.enqueue({"id": 1})
        self.assertEqual(q.batch_process(0), [])
        self.assertEqual(len(q), 1)


if __name__ == "__main__":
    unittest.main()
