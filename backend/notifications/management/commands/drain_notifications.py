"""
drain the in memory notification queue into Notification rows.

ref: lab 3 ex 2 NotificationQueue.batch_process. usage:
    python manage.py drain_notifications --max 500 --loop --interval 5
"""

import time

from django.core.management.base import BaseCommand

from notifications import services


class Command(BaseCommand):
    help = "drain the lab 3 notification queue into the database"

    def add_arguments(self, parser):
        parser.add_argument("--max", type=int, default=500,
                            help="max events per drain pass")
        parser.add_argument("--loop", action="store_true",
                            help="keep draining forever, sleeping --interval seconds")
        parser.add_argument("--interval", type=float, default=5.0,
                            help="seconds to sleep between passes when --loop is set")

    def handle(self, *args, **opts):
        if not opts["loop"]:
            objs = services.drain(max_events=opts["max"])
            self.stdout.write(self.style.SUCCESS(f"drained {len(objs)} notifications"))
            return
        self.stdout.write("loop mode: ctrl-c to stop")
        try:
            while True:
                objs = services.drain(max_events=opts["max"])
                if objs:
                    self.stdout.write(f"drained {len(objs)}")
                time.sleep(opts["interval"])
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("stopped"))
