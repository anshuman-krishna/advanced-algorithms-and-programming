"""
push notifications onto the lab 3 queue when likes, comments, or follows happen.

ref: claude.md phase 5. lab 3 ex 2 NotificationQueue.enqueue / priority_enqueue.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from posts.models import Comment, CommentLike, Like
from social.models import Follow

from . import services


@receiver(post_save, sender=Like)
def on_like_created(sender, instance, created, **kwargs):
    if not created:
        return
    services.enqueue_event(
        recipient_id=instance.post.author_id,
        actor_id=instance.user_id,
        kind="like",
        post_id=instance.post_id,
    )


@receiver(post_save, sender=Comment)
def on_comment_created(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.parent_id is None:
        # top level comment notifies the post author
        services.enqueue_event(
            recipient_id=instance.post.author_id,
            actor_id=instance.author_id,
            kind="comment",
            post_id=instance.post_id,
            comment_id=instance.id,
        )
    else:
        # reply notifies the parent comment's author with priority
        services.enqueue_event(
            recipient_id=instance.parent.author_id,
            actor_id=instance.author_id,
            kind="reply",
            post_id=instance.post_id,
            comment_id=instance.id,
            is_priority=True,
        )


@receiver(post_save, sender=Follow)
def on_follow_created(sender, instance, created, **kwargs):
    if not created:
        return
    services.enqueue_event(
        recipient_id=instance.following_id,
        actor_id=instance.follower_id,
        kind="follow",
    )


@receiver(post_save, sender=CommentLike)
def on_comment_like_created(sender, instance, created, **kwargs):
    """ref: lab 3 ex 2 enqueue. comment author gets notified when liked."""
    if not created:
        return
    services.enqueue_event(
        recipient_id=instance.comment.author_id,
        actor_id=instance.user_id,
        kind="like",
        post_id=instance.comment.post_id,
        comment_id=instance.comment_id,
    )
