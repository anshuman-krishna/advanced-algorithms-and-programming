"""
notification persistence model.

ref: claude.md section 5.3 (lab 3 queues for background notifications).
ref: lab 3 ex 2 NotificationQueue. the in memory queue lives in
algorithms/notification_queue.py; this table is the durable mirror so we can
restore the queue on boot and serve a list view.
"""

from django.conf import settings
from django.db import models


class Notification(models.Model):
    KIND_LIKE = "like"
    KIND_COMMENT = "comment"
    KIND_REPLY = "reply"
    KIND_FOLLOW = "follow"
    KIND_CHOICES = [
        (KIND_LIKE, "like"),
        (KIND_COMMENT, "comment"),
        (KIND_REPLY, "reply"),
        (KIND_FOLLOW, "follow"),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="emitted_notifications",
    )
    kind = models.CharField(max_length=16, choices=KIND_CHOICES)
    post_id = models.PositiveIntegerField(null=True, blank=True)
    comment_id = models.PositiveIntegerField(null=True, blank=True)
    is_priority = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "-created_at"]),
            models.Index(fields=["recipient", "is_read"]),
        ]

    def __str__(self):
        return f"{self.kind} from {self.actor_id} to {self.recipient_id}"
