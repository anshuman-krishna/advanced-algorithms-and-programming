"""
ops dashboard endpoint.

ref: phase 7 follow-up. surfaces index_stats, heap size, follow graph and
bst stats, reels dll size, segment tree cache, geo quadtree size, and the
notification queue counters in one payload. used by the mid-project demo so
the audience can read every cache state in one place.
"""

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView


class OpsDashboardView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from algorithms.follow_graph import _graph
        from algorithms.user_bst import _index as bst_index
        from algorithms.max_heap import get_trending_heap, is_hydrated
        from algorithms.doubly_linked_list import get_reels_list

        from search import services as search_services
        from analytics import services as analytics_services
        from geo import services as geo_services
        from notifications.services import queue_stats

        from search.models import Category, Hashtag

        heap = get_trending_heap()
        dll = get_reels_list()

        category_count = Category.objects.count()
        # category coverage = posts that landed under at least one category
        from search.models import PostCategory
        from posts.models import Post
        covered = (
            PostCategory.objects.values_list("post_id", flat=True).distinct().count()
        )
        total_posts = Post.objects.count()
        coverage_ratio = (covered / total_posts) if total_posts else 0.0

        return Response({
            "search_index": search_services.index_stats(),
            "trending_heap": {
                "hydrated": is_hydrated(),
                "size": len(heap),
            },
            "reels_dll": {"size": len(dll)},
            "follow_graph": {
                "users": _graph.num_users(),
                "edges": _graph.num_edges,
                "hydrated": _graph.is_hydrated(),
            },
            "user_bst": bst_index.stats(),
            "analytics_segment_trees": analytics_services.stats(),
            "geo_quadtree": geo_services.stats(),
            "notifications_queue": queue_stats(),
            "categories": {
                "count": category_count,
                "covered_posts": covered,
                "total_posts": total_posts,
                "coverage": coverage_ratio,
                "hashtags": Hashtag.objects.count(),
            },
        })
