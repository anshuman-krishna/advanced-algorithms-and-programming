"""
keep the per-user segment tree in sync with Like writes.

ref: lab 8 ex 3 point_update on each insert / delete.
"""

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from posts.models import Comment, Like

from . import services


@receiver(post_save, sender=Like)
def on_like_created(sender, instance, created, **kwargs):
    if not created:
        return
    services.record_like(instance.post.author_id, instance.created_at.date())


@receiver(post_delete, sender=Like)
def on_like_deleted(sender, instance, **kwargs):
    services.revoke_like(instance.post.author_id, instance.created_at.date())


@receiver(post_save, sender=Comment)
def on_comment_created(sender, instance, created, **kwargs):
    if not created:
        return
    services.record_comment(instance.post.author_id, instance.created_at.date())


@receiver(post_delete, sender=Comment)
def on_comment_deleted(sender, instance, **kwargs):
    services.revoke_comment(instance.post.author_id, instance.created_at.date())
