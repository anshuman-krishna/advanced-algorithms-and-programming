"""
pre-build the per-user segment tree for every active author so the first
/api/analytics/users/<id>/likes-range/ request is hot.

ref: lab 8 ex 3 segment tree. usage: python manage.py warm_analytics
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from analytics import services as analytics_svcs


class Command(BaseCommand):
    help = "pre-build the analytics segment tree for every user"

    def add_arguments(self, parser):
        parser.add_argument("--only", nargs="*", type=str,
                            help="usernames or ids to limit warming to")

    def handle(self, *args, **opts):
        User = get_user_model()
        qs = User.objects.all()
        if opts["only"]:
            ids = []
            usernames = []
            for raw in opts["only"]:
                if raw.isdigit():
                    ids.append(int(raw))
                else:
                    usernames.append(raw)
            qs = qs.filter(id__in=ids) | qs.filter(username__in=usernames)
        warmed = 0
        for user in qs:
            tree = analytics_svcs.get_tree(user.id)
            warmed += 1
            self.stdout.write(
                f"@{user.username}: total likes in window {int(tree.total())}",
            )
        self.stdout.write(self.style.SUCCESS(
            f"warmed {warmed} segment tree(s); cache holds {analytics_svcs.stats()['users_cached']}",
        ))
