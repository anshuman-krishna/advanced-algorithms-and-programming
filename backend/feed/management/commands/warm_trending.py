"""
pre-hydrate the trending max heap during deploy so the first /api/feed/trending
request does not pay the scan cost.

ref: lab 8 ex 2 max heap. usage: python manage.py warm_trending --window-hours 72 --k 50
"""

from django.core.management.base import BaseCommand

from feed import services as feed_services


class Command(BaseCommand):
    help = "pre-hydrate the trending max heap"

    def add_arguments(self, parser):
        parser.add_argument("--window-hours", type=int, default=72)
        parser.add_argument("--k", type=int, default=50)

    def handle(self, *args, **opts):
        items = feed_services.build_trending_feed(
            k=opts["k"], window_hours=opts["window_hours"], force=True,
        )
        self.stdout.write(self.style.SUCCESS(
            f"trending heap warm with top {len(items)} posts "
            f"(window {opts['window_hours']}h)"
        ))
