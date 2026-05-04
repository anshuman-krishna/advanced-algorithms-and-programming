"""
keep the geo quadtree in sync with Post writes.

ref: lab 7 ex 1 quadtree, fed by django signals so the tree never goes stale.
"""

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from posts.models import Post

from . import services


@receiver(post_save, sender=Post)
def on_post_saved(sender, instance, created, **kwargs):
    services.upsert_post(instance)


@receiver(post_delete, sender=Post)
def on_post_deleted(sender, instance, **kwargs):
    services.remove_post(instance.id)
