import os
import threading

from django.apps import AppConfig


class SocialConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "social"

    def ready(self):
        # register signal handlers on app boot
        from . import signals  # noqa: F401

        # hydrate the lab 6 adjacency list and the lab 8 ex 1 user bst on
        # boot, but off the request path so the first incoming request is
        # never billed for the full follow graph scan.
        # the test runner and management commands skip the warmup since they
        # either reset the singletons themselves or do not need the cache.
        if os.environ.get("AAP_DISABLE_WARMUP") or "test" in os.sys.argv[1:2]:
            return

        def _warmup():
            try:
                from algorithms.follow_graph import hydrate_from_db as warm_graph
                from algorithms.user_bst import hydrate_from_db as warm_bst
                warm_graph()
                warm_bst()
            except Exception:
                # cache warmups must never break boot; signals will hydrate
                # on first read if this thread fails
                pass

        threading.Thread(target=_warmup, name="social-warmup", daemon=True).start()
