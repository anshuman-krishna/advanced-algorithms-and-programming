"""
keep the reels doubly linked list in sync with Post writes.

ref: claude.md section 5.3 (lab 3 doubly linked lists for the reels fetcher).
ref: lab 3 ex 1 insert_after / remove_story.
"""

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from posts.models import Post

from . import services


@receiver(post_save, sender=Post)
def on_post_saved(sender, instance, created, **kwargs):
    if created:
        services.insert_post(instance)
    else:
        # caption / image edited; refresh the payload in place
        services.insert_post(instance)


@receiver(post_delete, sender=Post)
def on_post_deleted(sender, instance, **kwargs):
    services.remove_post(instance.id)
