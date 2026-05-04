from django.apps import AppConfig


class ReelsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "reels"

    def ready(self):
        # ref: lab 3 ex 1 doubly linked list. signals keep the in memory list
        # in sync with Post writes so the swipe cursor never goes stale.
        from . import signals  # noqa: F401
