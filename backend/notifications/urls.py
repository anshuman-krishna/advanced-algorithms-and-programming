from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import NotificationViewSet, QueueStatsView

router = DefaultRouter()
router.register(r"", NotificationViewSet, basename="notification")

urlpatterns = [
    path("queue/stats/", QueueStatsView.as_view(), name="notifications_queue_stats"),
    path("", include(router.urls)),
]
