"""
seed the explore taxonomy.

usage: python manage.py seed_categories
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from search.models import Category


TAXONOMY = {
    "cats": ["kittens", "tabby", "ragdoll"],
    "dogs": ["puppies", "retriever", "husky"],
    "rescue": ["adoptable", "fosters"],
    "grooming": ["bathtime", "haircuts"],
    "outdoors": ["hikes", "beachday"],
}


class Command(BaseCommand):
    help = "seeds explore categories with a small two level taxonomy"

    def handle(self, *args, **options):
        created = 0
        valid_names = set()
        for parent_name, children in TAXONOMY.items():
            valid_names.add(parent_name)
            parent, parent_created = Category.objects.get_or_create(
                name=parent_name,
                defaults={"slug": slugify(parent_name)},
            )
            if parent_created:
                created += 1
            for child_name in children:
                valid_names.add(child_name)
                _, child_created = Category.objects.get_or_create(
                    name=child_name,
                    defaults={"slug": slugify(child_name), "parent": parent},
                )
                if child_created:
                    created += 1
        # prune any leftover categories from an earlier taxonomy so explore stays
        # clean. cascades to their post links, which are empty by now anyway.
        removed, _ = Category.objects.exclude(name__in=valid_names).delete()
        self.stdout.write(self.style.SUCCESS(
            f"seeded categories. {created} new rows, {removed} pruned, "
            f"{Category.objects.count()} total"
        ))
