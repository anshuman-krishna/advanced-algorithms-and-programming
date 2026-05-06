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
        # boolean operators ('|', leading '-') stay on the legacy code path.
        # plain queries get tf-idf ranked. ref: lab 1 + standard tf-idf weighting.
        if "|" in query or any(t.startswith("-") for t in query.split()):
            ids = services.search_posts(query)
            scores = {pid: 0.0 for pid in ids}
        else:
            ranked = services.search_posts_ranked(query)
            ids = [pid for pid, _ in ranked]
            scores = dict(ranked)
        if not ids:
            return Response({"query": query, "count": 0, "results": []})
        posts_qs = Post.objects.filter(id__in=ids).select_related("author")
        ordered = sorted(posts_qs, key=lambda p: ids.index(p.id))
        serialized = PostSerializer(ordered, many=True, context={"request": request}).data
        for entry, post in zip(serialized, ordered):
            if scores.get(post.id):
                entry["search_score"] = scores[post.id]
        return Response({
            "query": query,
            "count": len(ordered),
            "results": serialized,
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
        response = Response({
            "prefix": prefix,
            "results": [
                {"username": key, "user_id": payload, "weight": weight}
                for key, payload, weight in hits
            ],
        })
        # autocomplete fires on every keystroke; the trie state changes only
        # on user signup so a 30s edge cache is safe and saves the chatter
        response["Cache-Control"] = "public, max-age=30"
        return response


class TrendingHashtagsView(APIView):
    """
    GET /api/search/hashtags/trending/?limit=

    surfaces the top n hashtags by post_count, sorted desc. ref: lab 8 ex 3
    trie weight; we read straight from the Hashtag table because the
    `post_count` column is exactly the weight we want.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        limit = _bounded_int(request.query_params.get("limit"), 10, 1, 50)
        rows = (
            Hashtag.objects.filter(post_count__gt=0)
            .order_by("-post_count", "name")
            .values("id", "name", "post_count")[:limit]
        )
        response = Response({
            "results": [
                {"hashtag": row["name"], "hashtag_id": row["id"],
                 "post_count": row["post_count"]}
                for row in rows
            ],
        })
        response["Cache-Control"] = "public, max-age=60"
        return response


class HashtagAutocompleteView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        prefix = request.query_params.get("q", "").lower().lstrip("#")
        if not prefix:
            return Response({"results": []})
        limit = _bounded_int(request.query_params.get("limit"), 10, 1, 50)
        hits = services.autocomplete_hashtags(prefix, limit=limit)
        response = Response({
            "prefix": prefix,
            "results": [
                {"hashtag": key, "hashtag_id": payload, "post_count": weight}
                for key, payload, weight in hits
            ],
        })
        response["Cache-Control"] = "public, max-age=30"
        return response


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


class HashtagRelatedView(APIView):
    """
    GET /api/search/hashtag/<name>/related/?limit=

    ref: lab 2 ex 2 jaccard similarity. for each other hashtag we compute
    jaccard over the set of users that liked any post tagged with the given
    name vs the users who liked posts under the candidate tag, then return
    the top k by similarity. surfaces "if you liked #X you may like #Y" hooks.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, name):
        from algorithms.sets_ops import jaccard_similarity
        from posts.models import Like

        normalized = name.lower().lstrip("#")
        anchor = Hashtag.objects.filter(name=normalized).first()
        if anchor is None:
            return Response({"hashtag": normalized, "results": []})
        limit = _bounded_int(request.query_params.get("limit"), 10, 1, 50)

        # users who liked posts tagged with `name`
        anchor_users = set(
            Like.objects.filter(
                post_id__in=PostHashtag.objects.filter(hashtag=anchor).values_list("post_id", flat=True),
            ).values_list("user_id", flat=True)
        )
        if not anchor_users:
            return Response({"hashtag": normalized, "results": []})

        # candidate tags: every other tag with at least one shared post or shared liker
        results = []
        for other in Hashtag.objects.exclude(id=anchor.id):
            other_users = set(
                Like.objects.filter(
                    post_id__in=PostHashtag.objects.filter(hashtag=other).values_list("post_id", flat=True),
                ).values_list("user_id", flat=True)
            )
            if not other_users:
                continue
            sim = jaccard_similarity(anchor_users, other_users)
            if sim > 0:
                results.append({
                    "hashtag": other.name,
                    "post_count": other.post_count,
                    "similarity": sim,
                })
        results.sort(key=lambda r: r["similarity"], reverse=True)
        return Response({
            "hashtag": normalized,
            "anchor_likers": len(anchor_users),
            "results": results[:limit],
        })


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
