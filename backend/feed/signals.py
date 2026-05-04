"""
invalidate the trending heap when likes or posts mutate.
"""

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from posts.models import Like, Post

from . import services


@receiver([post_save, post_delete], sender=Like)
def on_like_change(sender, instance, **kwargs):
    services.invalidate_trending()


@receiver([post_save, post_delete], sender=Post)
def on_post_change(sender, instance, **kwargs):
    services.invalidate_trending()
