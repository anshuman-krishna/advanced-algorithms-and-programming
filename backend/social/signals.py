"""
keep the in memory adjacency list and bst in sync with the database.
"""

from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from algorithms.follow_graph import get_graph
from algorithms.user_bst import get_index

from .models import Follow

User = get_user_model()


@receiver(post_save, sender=User)
def on_user_saved(sender, instance, created, **kwargs):
    if created:
        get_graph().add_user(instance.id)
        get_index().insert_user(instance.id, instance.username)
    else:
        # username may have changed, refresh metadata only
        node = get_index().get(instance.id)
        if node is not None:
            node.username = instance.username


@receiver(post_delete, sender=User)
def on_user_deleted(sender, instance, **kwargs):
    get_graph().remove_user(instance.id)
    get_index().remove_user(instance.id)


@receiver(post_save, sender=Follow)
def on_follow_created(sender, instance, created, **kwargs):
    if not created:
        return
    get_graph().add_edge(instance.follower_id, instance.following_id)
    get_index().add_friend(instance.follower_id, instance.following_id)


@receiver(post_delete, sender=Follow)
def on_follow_deleted(sender, instance, **kwargs):
    get_graph().remove_edge(instance.follower_id, instance.following_id)
    get_index().remove_friend(instance.follower_id, instance.following_id)
