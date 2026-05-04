"""
notification list, mark-read, and queue stats endpoints.

ref: claude.md phase 5. lab 3 ex 2 NotificationQueue exposed over rest.
"""

from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from . import services
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # drain on every list call so the in memory queue cannot grow forever
        services.drain()
        return (
            Notification.objects
            .filter(recipient=self.request.user)
            .select_related("actor")
        )

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        updated = (
            Notification.objects
            .filter(recipient=request.user, is_read=False)
            .update(is_read=True)
        )
        return Response({"marked_read": updated})

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        n = self.get_queryset().filter(pk=pk).first()
        if n is None:
            return Response({"detail": "not found"}, status=404)
        if not n.is_read:
            n.is_read = True
            n.save(update_fields=["is_read"])
        return Response(NotificationSerializer(n).data)

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        services.drain()
        count = (
            Notification.objects
            .filter(recipient=request.user, is_read=False)
            .count()
        )
        return Response({"unread": count})


class QueueStatsView(APIView):
    """ref: lab 3 ex 2 stats. exposes pending and processed counters."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(services.queue_stats())

    def post(self, request):
        # explicit drain trigger for ops dashboards
        objs = services.drain()
        return Response({"drained": len(objs)})
