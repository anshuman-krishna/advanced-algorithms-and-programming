"""
hydrate the in memory reels doubly linked list from the latest posts.

ref: lab 3 ex 1 doubly linked list hydrate. usage:
    python manage.py warm_reels --window 200
"""

from django.core.management.base import BaseCommand

from reels import services


class Command(BaseCommand):
    help = "preload the reels dll from the most recent posts"

    def add_arguments(self, parser):
        parser.add_argument("--window", type=int, default=services.DEFAULT_WINDOW,
                            help="how many recent posts to load")
        parser.add_argument("--reset", action="store_true",
                            help="clear the dll first before reloading")

    def handle(self, *args, **opts):
        if opts["reset"]:
            services.force_reset()
        size = services.hydrate_from_db(window=opts["window"])
        self.stdout.write(self.style.SUCCESS(f"reels dll size: {size}"))
