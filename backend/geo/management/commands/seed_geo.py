"""
attach demo coordinates to existing posts and rehydrate the quadtree.

usage: python manage.py seed_geo

picks a small list of well-known cities and round-robins them across the
posts that do not already have lat/lng. then forces a quadtree rehydrate.
"""

from django.core.management.base import BaseCommand

from posts.models import Post

from geo import services


CITIES = [
    ("Lisbon", 38.7223, -9.1393),
    ("New York", 40.7128, -74.0060),
    ("Tokyo", 35.6762, 139.6503),
    ("Sydney", -33.8688, 151.2093),
    ("Mumbai", 19.0760, 72.8777),
    ("Sao Paulo", -23.5505, -46.6333),
    ("Cape Town", -33.9249, 18.4241),
    ("Reykjavik", 64.1466, -21.9426),
]


class Command(BaseCommand):
    help = "round robin city coordinates onto demo posts"

    def add_arguments(self, parser):
        parser.add_argument("--overwrite", action="store_true",
                            help="apply coords even to posts that already have them")

    def handle(self, *args, **opts):
        qs = Post.objects.all().order_by("id")
        if not opts["overwrite"]:
            qs = qs.filter(latitude__isnull=True, longitude__isnull=True)
        applied = 0
        for i, post in enumerate(qs):
            city, lat, lng = CITIES[i % len(CITIES)]
            post.latitude = lat
            post.longitude = lng
            if not post.location:
                post.location = city
            post.save(update_fields=["latitude", "longitude", "location"])
            applied += 1
        size = services.hydrate_from_db()
        self.stdout.write(self.style.SUCCESS(
            f"applied coords to {applied} posts; quadtree size {size}",
        ))
