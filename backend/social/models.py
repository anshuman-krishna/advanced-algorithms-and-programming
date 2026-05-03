"""
follow edge model. graph operations live in algorithms/follow_graph.py.

ref: claude.md section 4.1 (followers entity).
ref: lab 6 ex 1 SocialGraph.add_friendship_list (we persist edges, not in memory).
"""

from django.conf import settings
from django.db import models


class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following",
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followers",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # one directed edge per ordered pair
            models.UniqueConstraint(
                fields=["follower", "following"], name="unique_follow_edge"
            ),
            # no self loops, matches the lab 6 implicit assumption
            models.CheckConstraint(
                check=~models.Q(follower=models.F("following")),
                name="no_self_follow",
            ),
        ]
        indexes = [
            models.Index(fields=["follower"]),
            models.Index(fields=["following"]),
        ]

    def __str__(self):
        return f"{self.follower_id} -> {self.following_id}"
