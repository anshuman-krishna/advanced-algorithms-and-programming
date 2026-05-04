"""
analytics endpoints over the segment tree.

ref: claude.md phase 6. lab 8 ex 3 prefix and range trees applied to per-user
daily likes.
"""

from datetime import date, datetime, timedelta

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services


User = get_user_model()


def _resolve_user(identifier: str):
    if identifier.isdigit():
        return get_object_or_404(User, pk=int(identifier))
    return get_object_or_404(User, username=identifier)


def _parse_date(raw: str, default: date) -> date:
    if not raw:
        return default
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        return default


class LikesRangeView(APIView):
    """
    GET /api/analytics/users/<id|username>/likes-range/?from=YYYY-MM-DD&to=YYYY-MM-DD

    ref: lab 8 ex 3 range_sum. defaults: last 30 days.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, identifier):
        user = _resolve_user(identifier)
        today = date.today()
        end = _parse_date(request.query_params.get("to", ""), today)
        start = _parse_date(
            request.query_params.get("from", ""), end - timedelta(days=29),
        )
        if start > end:
            start, end = end, start
        total = services.likes_in_range(user.id, start, end)
        return Response({
            "user_id": user.id,
            "username": user.username,
            "from": start.isoformat(),
            "to": end.isoformat(),
            "days": (end - start).days + 1,
            "total_likes": int(total),
        })


class LikesSeriesView(APIView):
    """
    GET /api/analytics/users/<id|username>/likes-series/

    full daily histogram for the configured window. small payload, easy plot.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, identifier):
        user = _resolve_user(identifier)
        series = services.daily_series(user.id)
        meta = services.stats()
        return Response({
            "user_id": user.id,
            "username": user.username,
            "origin": meta["origin"],
            "window_days": meta["window_days"],
            "series": [int(v) for v in series],
        })


class AnalyticsStatsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(services.stats())

    def post(self, request):
        services.reset()
        return Response({"reset": True, **services.stats()})
