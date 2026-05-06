"""
snapshot the in-memory search and analytics caches to disk.

ref: phase 6 follow-up. usage: python manage.py dump_caches
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "persist in-memory search index, tries, and analytics segment trees"

    def handle(self, *args, **opts):
        from django.core.management import call_command
        from algorithms.inverted_index import ensure_hydrated as ensure_index
        from algorithms.trie import ensure_hashtag_trie, ensure_user_trie
        from search import persistence as search_persistence
        from analytics import persistence as analytics_persistence
        from analytics import services as analytics_services

        # make sure the in-memory structures are hot before snapshotting
        call_command("rebuild_search_index")
        ensure_index()
        ensure_user_trie()
        ensure_hashtag_trie()
        call_command("warm_analytics")

        report = search_persistence.save_all()
        self.stdout.write(self.style.SUCCESS(
            f"search snapshot: {report['documents']} docs, {report['terms']} terms",
        ))
        analytics_report = analytics_persistence.save(analytics_services._trees)
        self.stdout.write(self.style.SUCCESS(
            f"analytics snapshot: {analytics_report['users']} segment trees",
        ))
