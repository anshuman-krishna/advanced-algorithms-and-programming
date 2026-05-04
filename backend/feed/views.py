from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services


class HomeFeedView(APIView):
    """
    personalized timeline.

    ref: claude.md phase 3. lab 3 ex 3 priority queue, lab 1 linear time slicing.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            offset = max(0, int(request.query_params.get("offset", 0)))
            limit = max(1, min(100, int(request.query_params.get("limit", 20))))
            window = max(1, min(720, int(request.query_params.get("window_hours", 72))))
        except (TypeError, ValueError):
            return Response({"detail": "offset, limit, window_hours must be integers"}, status=400)

        results = services.build_home_feed(
            request.user.id, offset=offset, limit=limit, window_hours=window
        )
        return Response({
            "strategy": "linked_list_priority_queue",
            "offset": offset,
            "limit": limit,
            "results": results,
        })


class TrendingFeedView(APIView):
    """
    global top k trending posts.

    ref: claude.md phase 3. lab 8 ex 2 binary heap.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        try:
            k = max(1, min(100, int(request.query_params.get("k", 10))))
            window = max(1, min(720, int(request.query_params.get("window_hours", 72))))
            force = request.query_params.get("force") in ("1", "true", "True")
        except (TypeError, ValueError):
            return Response({"detail": "k and window_hours must be integers"}, status=400)

        results = services.build_trending_feed(k=k, window_hours=window, force=force)
        return Response({
            "strategy": "binary_max_heap",
            "k": k,
            "results": results,
        })


class ReelsFeedView(APIView):
    """
    swipeable reels feed.

    ref: claude.md phase 5. lab 3 ex 1 doubly linked list cursor based traversal.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        try:
            limit = max(1, min(50, int(request.query_params.get("limit", 5))))
            window = max(1, min(720, int(request.query_params.get("window_hours", 72))))
            cursor_raw = request.query_params.get("cursor")
            cursor = int(cursor_raw) if cursor_raw not in (None, "") else None
            direction = request.query_params.get("direction", "next")
            if direction not in ("next", "prev"):
                return Response({"detail": "direction must be next or prev"}, status=400)
            force = request.query_params.get("force") in ("1", "true", "True")
        except (TypeError, ValueError):
            return Response(
                {"detail": "limit, window_hours, and cursor must be integers"},
                status=400,
            )

        page = services.build_reels_page(
            cursor=cursor,
            direction=direction,
            limit=limit,
            window_hours=window,
            force=force,
        )
        return Response({"strategy": "doubly_linked_list", **page})

    def post(self, request):
        """track a view on the supplied post id (lab 3 ex 1 track_view)."""
        try:
            post_id = int(request.data.get("post_id"))
        except (TypeError, ValueError):
            return Response({"detail": "post_id is required"}, status=400)
        views = services.reels_track_view(post_id)
        return Response({"post_id": post_id, "views": views})


class ReelsMostViewedView(APIView):
    """ref: lab 3 ex 1 most_viewed."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        most = services.reels_most_viewed()
        return Response({"most_viewed": most})
