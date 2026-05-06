"""
pre-build the recursive comment tree for one or more posts so the first
/api/posts/posts/<id>/thread/ request is hot.

usage:
  python manage.py warm_threads 4 5 6
  python manage.py warm_threads --all-with-comments
"""

from django.core.management.base import BaseCommand

from posts.models import Comment, Post
from posts import services_threads


class Command(BaseCommand):
    help = "pre-build the recursive comment tree for the given post ids"

    def add_arguments(self, parser):
        parser.add_argument("post_ids", nargs="*", type=int)
        parser.add_argument(
            "--all-with-comments",
            action="store_true",
            help="warm every post that has at least one comment",
        )

    def handle(self, *args, **opts):
        ids = list(opts["post_ids"])
        if opts["all_with_comments"]:
            ids.extend(
                Comment.objects.values_list("post_id", flat=True).distinct(),
            )
        ids = sorted(set(ids))
        if not ids:
            self.stdout.write("no post ids supplied")
            return
        for post_id in ids:
            if not Post.objects.filter(pk=post_id).exists():
                self.stdout.write(self.style.WARNING(f"post {post_id} missing, skipped"))
                continue
            metrics = services_threads.thread_metrics(post_id)
            services_threads.thread_for_post(post_id)
            self.stdout.write(self.style.SUCCESS(
                f"post {post_id}: count={metrics['count']} depth={metrics['max_depth']} "
                f"likes={metrics['total_likes']}"
            ))
