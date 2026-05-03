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
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, identifier, kind):
        user = _resolve_user(identifier)
        if kind == "followers":
            ids = services.get_followers(user.id)
        elif kind == "following":
            ids = services.get_following(user.id)
        else:
            return Response({"detail": "unknown kind"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"count": len(ids), "results": _users_payload(ids)})


class RelationshipView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, identifier, other):
        a = _resolve_user(identifier)
        b = _resolve_user(other)
        return Response({
            "a_follows_b": services.is_following(a.id, b.id),
            "b_follows_a": services.is_following(b.id, a.id),
            "mutual_followers": list(services.mutual_followers_of(a.id, b.id)),
            "shared_following": list(services.shared_following_of(a.id, b.id)),
            "follower_jaccard": services.follower_jaccard(a.id, b.id),
        })


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
