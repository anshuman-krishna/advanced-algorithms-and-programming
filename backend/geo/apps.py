from django.apps import AppConfig


class GeoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "geo"

    def ready(self):
        # ref: lab 7 ex 1 quadtree, kept warm via Post signals
        from . import signals  # noqa: F401
