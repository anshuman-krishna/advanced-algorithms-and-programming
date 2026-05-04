"""
seed the explore taxonomy.

usage: python manage.py seed_categories
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from search.models import Category


TAXONOMY = {
    "sports": ["football", "running", "cycling"],
    "fashion": ["streetwear", "vintage"],
    "tech": ["ai", "hardware", "software"],
    "music": ["synth", "live"],
    "travel": ["lisbon", "tokyo"],
}


class Command(BaseCommand):
    help = "seeds explore categories with a small two level taxonomy"

    def handle(self, *args, **options):
        created = 0
        for parent_name, children in TAXONOMY.items():
            parent, parent_created = Category.objects.get_or_create(
                name=parent_name,
                defaults={"slug": slugify(parent_name)},
            )
            if parent_created:
                created += 1
            for child_name in children:
                _, child_created = Category.objects.get_or_create(
                    name=child_name,
                    defaults={"slug": slugify(child_name), "parent": parent},
                )
                if child_created:
                    created += 1
        self.stdout.write(self.style.SUCCESS(
            f"seeded categories. {created} new rows, {Category.objects.count()} total"
        ))
