from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from posts.models import Post
from posts.serializers import PostSerializer

from . import services
from .models import Hashtag, PostHashtag

User = get_user_model()


def _bounded_int(value, default, low, high):
    try:
        n = int(value)
    except (TypeError, ValueError):
        return default
    return max(low, min(high, n))


class PostSearchView(APIView):
    """ref: claude.md phase 4 inverted index search."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response({"detail": "q is required"}, status=400)
        ids = services.search_posts(query)
        if not ids:
            return Response({"query": query, "count": 0, "results": []})
        posts_qs = Post.objects.filter(id__in=ids).select_related("author")
        # preserve search rank ordering when returning
        ordered = sorted(posts_qs, key=lambda p: ids.index(p.id))
        return Response({
            "query": query,
            "count": len(ordered),
            "results": PostSerializer(ordered, many=True, context={"request": request}).data,
        })


class UsernameAutocompleteView(APIView):
    """ref: claude.md phase 4 trie autocomplete (lab 8 ex 3)."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        prefix = request.query_params.get("q", "").lower().lstrip("@")
        if not prefix:
            return Response({"results": []})
        limit = _bounded_int(request.query_params.get("limit"), 10, 1, 50)
        hits = services.autocomplete_users(prefix, limit=limit)
        return Response({
            "prefix": prefix,
            "results": [
                {"username": key, "user_id": payload, "weight": weight}
                for key, payload, weight in hits
            ],
        })


class HashtagAutocompleteView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        prefix = request.query_params.get("q", "").lower().lstrip("#")
        if not prefix:
            return Response({"results": []})
        limit = _bounded_int(request.query_params.get("limit"), 10, 1, 50)
        hits = services.autocomplete_hashtags(prefix, limit=limit)
        return Response({
            "prefix": prefix,
            "results": [
                {"hashtag": key, "hashtag_id": payload, "post_count": weight}
                for key, payload, weight in hits
            ],
        })


class ExploreTreeView(APIView):
    """ref: claude.md phase 4 generalized trees (lab 5)."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(services.explore_tree())


class CategoryEngagementView(APIView):
    """ref: claude.md phase 4 bottom up engagement (lab 5 ex 2)."""

    permission_classes = [permissions.AllowAny]

    def get(self, request, category_id):
        try:
            cid = int(category_id)
        except (TypeError, ValueError):
            return Response({"detail": "invalid category id"}, status=400)
        return Response(services.category_engagement(cid))


class RecommendationsView(APIView):
    """
    content based recommendations.

    ref: claude.md phase 4 collaborative filtering. lab 2 jaccard / cosine.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        strategy = request.query_params.get("strategy", "jaccard").lower()
        if strategy not in {"jaccard", "cosine"}:
            return Response({"detail": "strategy must be jaccard or cosine"}, status=400)
        limit = _bounded_int(request.query_params.get("limit"), 10, 1, 50)
        ranked = services.recommend_posts(request.user.id, strategy=strategy, max_results=limit)
        if not ranked:
            return Response({"strategy": strategy, "results": []})
        post_ids = [pid for pid, _ in ranked]
        posts_qs = Post.objects.filter(id__in=post_ids).select_related("author")
        posts_by_id = {p.id: p for p in posts_qs}
        results = []
        for pid, score in ranked:
            post = posts_by_id.get(pid)
            if post is None:
                continue
            entry = PostSerializer(post, context={"request": request}).data
            entry["similarity_score"] = score
            results.append(entry)
        return Response({"strategy": strategy, "results": results})


class IndexStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(services.index_stats())


class HashtagPostsView(APIView):
    """ref: claude.md phase 4. drill down a single hashtag to its posts."""

    permission_classes = [permissions.AllowAny]

    def get(self, request, name):
        normalized = name.lower().lstrip("#")
        tag = Hashtag.objects.filter(name=normalized).first()
        if tag is None:
            return Response({"hashtag": normalized, "post_count": 0, "results": []})
        limit = _bounded_int(request.query_params.get("limit"), 20, 1, 100)
        offset = _bounded_int(request.query_params.get("offset"), 0, 0, 10000)
        post_ids = list(
            PostHashtag.objects.filter(hashtag=tag)
            .order_by("-post__created_at")
            .values_list("post_id", flat=True)[offset:offset + limit]
        )
        if not post_ids:
            return Response({
                "hashtag": normalized,
                "hashtag_id": tag.id,
                "post_count": tag.post_count,
                "results": [],
            })
        posts_qs = Post.objects.filter(id__in=post_ids).select_related("author")
        ordered = sorted(posts_qs, key=lambda p: post_ids.index(p.id))
        return Response({
            "hashtag": normalized,
            "hashtag_id": tag.id,
            "post_count": tag.post_count,
            "offset": offset,
            "limit": limit,
            "results": PostSerializer(ordered, many=True, context={"request": request}).data,
        })
