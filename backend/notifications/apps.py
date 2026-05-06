import os
import threading

from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notifications"

    def ready(self):
        from . import signals  # noqa: F401

        # rehydrate the lab 3 ex 2 NotificationQueue from the sqlite spillover
        # so a process restart does not drop pending events. ref: phase 5
        # follow-up. we do this in a background thread so worker boot is not
        # billed for the disk read; tests skip the rehydrate via env var.
        if os.environ.get("AAP_DISABLE_WARMUP") or "test" in os.sys.argv[1:2]:
            return

        def _rehydrate():
            try:
                from . import services
                services.rehydrate_from_spillover()
            except Exception:
                pass

        threading.Thread(
            target=_rehydrate, name="notifications-rehydrate", daemon=True,
        ).start()
