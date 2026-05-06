"""
reset and rehydrate every in-memory cache that the project keeps warm:
adjacency list (lab 6 ex 1), bst index (lab 8 ex 1), reels dll (lab 3 ex 1),
trending heap (lab 8 ex 2), inverted index + tries (lab 1, lab 8 ex 3),
analytics segment trees (lab 8 ex 3), geo quadtree (lab 7 ex 1).

usage: python manage.py rebuild_caches
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "rebuild every in-memory cache from the database"

    def handle(self, *args, **opts):
        from algorithms.follow_graph import (
            _graph as graph_singleton,
            hydrate_from_db as hydrate_graph,
        )
        from algorithms.user_bst import (
            _index as bst_singleton,
            hydrate_from_db as hydrate_bst,
        )
        from algorithms.max_heap import mark_dirty as drop_trending
        from reels import services as reels_svcs
        from analytics import services as analytics_svcs
        from geo import services as geo_svcs

        graph_singleton.reset()
        hydrate_graph()
        self.stdout.write(self.style.SUCCESS(
            f"adjacency list: {graph_singleton.num_users()} users, "
            f"{graph_singleton.num_edges} edges",
        ))

        bst_singleton.reset()
        hydrate_bst()
        bst_stats = bst_singleton.stats()
        self.stdout.write(self.style.SUCCESS(
            f"bst index: {bst_stats.get('size', '?')} users",
        ))

        reels_svcs.force_reset()
        size = reels_svcs.hydrate_from_db()
        self.stdout.write(self.style.SUCCESS(f"reels dll: {size} posts"))

        drop_trending()
        self.stdout.write(self.style.SUCCESS("trending heap: marked dirty"))

        call_command("rebuild_search_index")

        analytics_svcs.reset()
        self.stdout.write(self.style.SUCCESS("analytics segment trees: cleared"))

        geo_svcs.force_reset()
        geo_size = geo_svcs.hydrate_from_db()
        self.stdout.write(self.style.SUCCESS(f"geo quadtree: {geo_size} posts"))
