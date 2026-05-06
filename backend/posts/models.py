"""
post, like, and comment models.

ref: claude.md section 4.1.
ref: lab 4 ex 1 (recursive comment thread traversal) for the parent fk on Comment.
"""

from django.conf import settings
from django.db import models


class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    image = models.ImageField(upload_to="posts/", null=True, blank=True)
    caption = models.TextField(blank=True, default="")
    location = models.CharField(max_length=255, blank=True, default="")
    # latitude and longitude reserved for the lab 7 quadtree work in phase 6
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["author", "-created_at"]),
        ]

    def __str__(self):
        return f"post {self.pk} by {self.author_id}"

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def comment_count(self):
        return self.comments.count()


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="liked_posts",
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # one like per user per post
        constraints = [
            models.UniqueConstraint(fields=["user", "post"], name="unique_user_post_like"),
        ]
        indexes = [
            models.Index(fields=["post", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.user_id} liked {self.post_id}"


class Comment(models.Model):
    """
    self referential parent fk so a comment may have unbounded children.
    ref: lab 4 ex 1 CommentNode.replies (we use a fk instead of an in memory list).
    """

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="authored_comments",
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies",
    )
    content = models.TextField()
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["post", "parent", "created_at"]),
        ]
        constraints = [
            # defense in depth on top of the recursive cycle guard in build_thread.
            # a comment must never reference itself as parent.
            models.CheckConstraint(
                check=~models.Q(parent_id=models.F("id")),
                name="comment_parent_not_self",
            ),
        ]

    def __str__(self):
        return f"comment {self.pk} on post {self.post_id}"

    @property
    def like_count(self):
        return self.comment_likes.count()


class CommentLike(models.Model):
    """
    one row per (user, comment) so total_likes on a thread is real.

    ref: lab 4 ex 1 CommentNode.likes attribute. the recursive aggregator
    sums these counts per subtree.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="liked_comments",
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="comment_likes",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "comment"], name="unique_user_comment_like"),
        ]
        indexes = [
            models.Index(fields=["comment", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.user_id} liked comment {self.comment_id}"
