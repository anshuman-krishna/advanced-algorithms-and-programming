from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import UserSerializer

from . import services
from .models import Follow
from .serializers import FollowSerializer

User = get_user_model()


def _resolve_user(identifier: str):
    """allow both numeric ids and usernames to address users."""
    if identifier.isdigit():
        return get_object_or_404(User, pk=int(identifier))
    return get_object_or_404(User, username=identifier)


def _users_payload(user_ids):
    qs = User.objects.filter(id__in=list(user_ids))
    return UserSerializer(qs, many=True).data


class FollowViewSet(viewsets.ModelViewSet):
    """
    follow and unfollow edges plus phase 2 graph queries.

    ref: claude.md phase 2.
    ref: lab 6 ex 1 (adjacency list), lab 2 ex 2 (mutual via sets),
         lab 8 ex 1 (bst friend of friend).
    """

    queryset = Follow.objects.select_related("follower", "following").all()
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        user_id = self.request.query_params.get("user")
        if user_id is not None:
            qs = qs.filter(follower_id=user_id)
        return qs

    def create(self, request, *args, **kwargs):
        target_id = request.data.get("following")
        if target_id is None:
            return Response({"detail": "following is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            target_id_int = int(target_id)
        except (TypeError, ValueError):
            return Response({"detail": "following must be an int id"}, status=status.HTTP_400_BAD_REQUEST)
        if target_id_int == request.user.id:
            return Response({"detail": "cannot follow yourself"}, status=status.HTTP_400_BAD_REQUEST)
        target = get_object_or_404(User, pk=target_id_int)
        edge, created = Follow.objects.get_or_create(
            follower=request.user, following=target
        )
        return Response(
            FollowSerializer(edge).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path=r"toggle/(?P<identifier>[^/.]+)",
            permission_classes=[permissions.IsAuthenticated])
    def toggle(self, request, identifier=None):
        """idempotent follow toggle. flips the edge state."""
        target = _resolve_user(identifier)
        if target.id == request.user.id:
            return Response({"detail": "cannot follow yourself"}, status=status.HTTP_400_BAD_REQUEST)
        edge = Follow.objects.filter(follower=request.user, following=target).first()
        if edge is None:
            services.follow_user(request.user.id, target.id)
            return Response({"following": True}, status=status.HTTP_201_CREATED)
        services.unfollow_user(request.user.id, target.id)
        return Response({"following": False}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path=r"unfollow/(?P<identifier>[^/.]+)",
            permission_classes=[permissions.IsAuthenticated])
    def unfollow(self, request, identifier=None):
        target = _resolve_user(identifier)
        deleted = services.unfollow_user(request.user.id, target.id)
        return Response({"removed": deleted})


class UserGraphView(APIView):
    """
    relationship surface for a single user.

    GET /api/social/users/<id|username>/followers/
    GET /api/social/users/<id|username>/following/
    GET /api/social/users/<id|username>/relationship/<other>/

    if `user.is_private` is true the follower / following list is only visible
    to the owner or to someone who already follows them. unauthorized callers
    receive a stub payload with `private: true` and an empty list.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, identifier, kind):
        user = _resolve_user(identifier)
        if kind not in ("followers", "following"):
            return Response({"detail": "unknown kind"}, status=status.HTTP_404_NOT_FOUND)

        viewer = request.user if request.user.is_authenticated else None
        if user.is_private:
            allowed = (
                viewer is not None
                and (viewer.id == user.id or services.is_following(viewer.id, user.id))
            )
            if not allowed:
                return Response({
                    "user_id": user.id,
                    "private": True,
                    "count": 0,
                    "results": [],
                })

        if kind == "followers":
            ids = services.get_followers(user.id)
        else:
            ids = services.get_following(user.id)
        response = Response({
            "user_id": user.id,
            "private": user.is_private,
            "count": len(ids),
            "results": _users_payload(ids),
        })
        # short edge cache so the frontend can short circuit duplicate
        # requests during a single session without waiting on the api
        response["Cache-Control"] = "private, max-age=30"
        return response


class RelationshipView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, identifier, other):
        a = _resolve_user(identifier)
        b = _resolve_user(other)
        response = Response({
            "a_follows_b": services.is_following(a.id, b.id),
            "b_follows_a": services.is_following(b.id, a.id),
            "mutual_followers": list(services.mutual_followers_of(a.id, b.id)),
            "shared_following": list(services.shared_following_of(a.id, b.id)),
            "follower_jaccard": services.follower_jaccard(a.id, b.id),
        })
        response["Cache-Control"] = "private, max-age=30"
        return response


class SuggestionsView(APIView):
    """
    friend of friend suggestions.
    primary path: bst ranking by mutual count (lab 8).
    fallback: set difference (lab 2) when the bst path is cold.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        max_suggestions = int(request.query_params.get("limit", 10))
        ranked = services.suggest_via_bst(request.user.id, max_suggestions=max_suggestions)
        if not ranked:
            ids = list(services.suggest_via_sets(request.user.id))[:max_suggestions]
            payload = _users_payload(ids)
            return Response({"strategy": "set_difference", "results": payload})
        ids = [user_id for user_id, _ in ranked]
        users_by_id = {u.id: u for u in User.objects.filter(id__in=ids)}
        results = []
        for user_id, mutual_count in ranked:
            user = users_by_id.get(user_id)
            if user is None:
                continue
            entry = UserSerializer(user).data
            entry["mutual_count"] = mutual_count
            results.append(entry)
        return Response({"strategy": "bst_friend_of_friend", "results": results})


class GraphStatsView(APIView):
    """debug surface for the in memory adjacency list and bst index."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            "adjacency_list": services.graph_stats(),
            "user_bst": services.index_stats(),
        })


class CommunitiesView(APIView):
    """
    GET /api/social/communities/

    ref: claude.md phase 6. lab 6 ex 2 dfs connected components on the
    undirected friendship view. returns clusters sorted by size desc.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        components = services.communities()
        return Response({
            "count": len(components),
            "components": [
                {"size": len(c), "members": c} for c in components
            ],
        })


class CommunityOfView(APIView):
    """GET /api/social/users/<id|username>/community/."""

    permission_classes = [permissions.AllowAny]

    def get(self, request, identifier):
        user = _resolve_user(identifier)
        members = services.community_of(user.id)
        return Response({
            "user_id": user.id,
            "username": user.username,
            "size": len(members),
            "members": members,
        })


class ShortestChainView(APIView):
    """
    GET /api/social/shortest-chain/?from=<id|username>&to=<id|username>

    ref: lab 6 ex 3 bfs shortest_path. returns [] if disconnected.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        src_raw = request.query_params.get("from")
        dst_raw = request.query_params.get("to")
        if not src_raw or not dst_raw:
            return Response({"detail": "from and to are required"}, status=400)
        src = _resolve_user(src_raw)
        dst = _resolve_user(dst_raw)
        chain = services.shortest_chain(src.id, dst.id)
        users_by_id = {u.id: u for u in User.objects.filter(id__in=chain)}
        return Response({
            "from": src.id,
            "to": dst.id,
            "length": max(0, len(chain) - 1),
            "chain": [
                {"id": uid, "username": users_by_id.get(uid).username if users_by_id.get(uid) else None}
                for uid in chain
            ],
        })


class ReachView(APIView):
    """
    GET /api/social/users/<id|username>/reach/?max_depth=

    ref: lab 6 ex 3 bfs_with_distances. groups users by hop distance so the
    frontend can paint a six-degrees-of-separation visualization.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, identifier):
        user = _resolve_user(identifier)
        max_depth = request.query_params.get("max_depth")
        try:
            depth = int(max_depth) if max_depth is not None else None
        except ValueError:
            return Response({"detail": "max_depth must be an integer"}, status=400)
        distances = services.bfs_distances(user.id, max_depth=depth)
        buckets = {}
        for user_id, hops in distances.items():
            buckets.setdefault(hops, []).append(user_id)
        layers = [
            {"depth": d, "user_ids": sorted(buckets[d]), "count": len(buckets[d])}
            for d in sorted(buckets.keys())
        ]
        return Response({
            "user_id": user.id,
            "username": user.username,
            "reach": len(distances),
            "layers": layers,
        })


class NichePostsView(APIView):
    """
    GET /api/social/users/<id|username>/niche-posts/?limit=

    ref: claude.md phase 6 dfs community detection -> niche content.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, identifier):
        user = _resolve_user(identifier)
        try:
            limit = max(1, min(int(request.query_params.get("limit", 20)), 100))
        except ValueError:
            limit = 20
        post_ids = services.niche_posts(user.id, limit=limit)
        return Response({
            "user_id": user.id,
            "limit": limit,
            "post_ids": post_ids,
        })
