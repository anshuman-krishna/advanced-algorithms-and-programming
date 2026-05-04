"""
reels endpoints.

ref: claude.md phase 5. lab 3 ex 1 doubly linked list page / jump_to / track_view /
most_viewed exposed over rest.
"""

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services


class ReelsPageView(APIView):
    """
    cursor pagination across the dll.

    ref: lab 3 ex 1 page. query params:
      cursor=<post_id>  optional anchor; first call should omit
      direction=next|prev (default next)
      limit=int (default 5, max 20)
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        cursor = request.query_params.get("cursor")
        direction = request.query_params.get("direction", "next")
        if direction not in ("next", "prev"):
            return Response({"detail": "direction must be next or prev"}, status=400)
        try:
            limit = min(int(request.query_params.get("limit", 5)), 20)
        except ValueError:
            return Response({"detail": "limit must be an integer"}, status=400)
        anchor = None
        if cursor:
            try:
                anchor = int(cursor)
            except ValueError:
                return Response({"detail": "cursor must be an integer"}, status=400)
        items, next_cursor = services.page(anchor, direction, limit)
        return Response({
            "results": items,
            "next_cursor": next_cursor,
            "direction": direction,
            "size": services.stats()["size"],
        })


class ReelsAroundView(APIView):
    """ref: lab 3 ex 1 display_around_current. /api/reels/around/<post_id>/?k=N."""

    permission_classes = [permissions.AllowAny]

    def get(self, request, post_id):
        try:
            k = min(int(request.query_params.get("k", 3)), 10)
        except ValueError:
            return Response({"detail": "k must be an integer"}, status=400)
        window = services.slice_around(post_id, k)
        if not window:
            return Response({"detail": "post not in reels list"}, status=404)
        return Response({"post_id": post_id, "window": window})


class ReelsViewedView(APIView):
    """ref: lab 3 ex 1 track_view. POST /api/reels/<post_id>/view/."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        node = services.track_view(post_id)
        if node is None:
            return Response({"detail": "post not in reels list"}, status=404)
        return Response({"post_id": post_id, "views": node["views"]})


class ReelsMostViewedView(APIView):
    """ref: lab 3 ex 1 most_viewed."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        node = services.most_viewed()
        if node is None:
            return Response({"detail": "reels list empty"}, status=404)
        return Response(node)


class ReelsStatsView(APIView):
    """ops endpoint: dll size, cursor, hydration state."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(services.stats())

    def post(self, request):
        # force hydrate or reset
        if request.query_params.get("reset") in ("1", "true"):
            services.force_reset()
        size = services.hydrate_from_db()
        return Response({"hydrated": True, "size": size})
