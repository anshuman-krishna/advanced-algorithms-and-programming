from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import services_threads
from .models import Comment, CommentLike, Like, Post
from .permissions import IsAuthorOrReadOnly
from .serializers import CommentSerializer, PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    """
    crud for posts.

    ref: claude.md phase 1.
    """

    queryset = Post.objects.select_related("author").all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        # unique constraint (user, post) makes this idempotent
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        return Response(
            {"liked": True, "like_count": post.likes.count(), "created": created},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def unlike(self, request, pk=None):
        post = self.get_object()
        deleted, _ = Like.objects.filter(user=request.user, post=post).delete()
        return Response({"liked": False, "like_count": post.likes.count(), "removed": deleted})

    @action(detail=True, methods=["get"])
    def comments(self, request, pk=None):
        """flat list of top level comments. nested traversal lives in `thread`."""
        post = self.get_object()
        top_level = post.comments.filter(parent__isnull=True).select_related("author")
        serializer = CommentSerializer(top_level, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def thread(self, request, pk=None):
        """
        full nested comment thread.

        ref: claude.md phase 5. lab 4 ex 1 recursive traversal, ex 2 aggregation,
        ex 3 explicit stack hint via ensure_recursion_limit.
        """
        post = self.get_object()
        prune = request.query_params.get("prune", "1") not in ("0", "false", "False")
        return Response({
            "post_id": post.id,
            "results": services_threads.thread_for_post(post.id, prune=prune),
        })

    @action(detail=True, methods=["get"], url_path="thread-stats")
    def thread_stats(self, request, pk=None):
        """count, max depth, total likes for the thread (lab 4 ex 1 + ex 2 aggregations)."""
        post = self.get_object()
        return Response({"post_id": post.id, **services_threads.thread_metrics(post.id)})

    @action(detail=True, methods=["get"], url_path="thread-search")
    def thread_search(self, request, pk=None):
        """
        recursive search across the thread.

        ref: lab 4 ex 1 search_by_user, contains_keyword. accepts ?q=<keyword>
        and/or ?user_id=<id>; if both are passed we union the matches.
        """
        post = self.get_object()
        keyword = request.query_params.get("q", "").strip()
        user_id_raw = request.query_params.get("user_id")
        results = []
        if keyword:
            results.extend(services_threads.search_thread_by_keyword(post.id, keyword))
        if user_id_raw:
            try:
                results.extend(services_threads.search_thread_by_user(post.id, int(user_id_raw)))
            except ValueError:
                return Response({"detail": "user_id must be an integer"}, status=400)
        # de-dup by comment id while preserving order
        seen = set()
        deduped = []
        for r in results:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            deduped.append(r)
        return Response({"post_id": post.id, "results": deduped})

    @action(detail=True, methods=["get"], url_path="thread-depth")
    def thread_depth(self, request, pk=None):
        """ref: lab 4 ex 1 find_deepest_reply across roots."""
        post = self.get_object()
        return Response({
            "post_id": post.id,
            "max_depth": services_threads.deepest_branch_depth(post.id),
        })

    @action(detail=True, methods=["get"], url_path="thread-count")
    def thread_count(self, request, pk=None):
        """ref: lab 4 ex 3 count_iterative. cheap inbox preview without serializing the tree."""
        post = self.get_object()
        return Response({
            "post_id": post.id,
            "count": services_threads.thread_count(post.id),
        })

    @action(detail=True, methods=["get"], url_path="thread-engagement")
    def thread_engagement(self, request, pk=None):
        """ref: lab 4 ex 2 divide and conquer aggregator with a swappable score."""
        post = self.get_object()
        score = request.query_params.get("score", "likes")
        if score not in ("likes", "recency"):
            return Response({"detail": "score must be 'likes' or 'recency'"}, status=400)
        return Response({
            "post_id": post.id,
            **services_threads.thread_engagement(post.id, score=score),
        })


class CommentViewSet(viewsets.ModelViewSet):
    """
    crud for comments. recursive thread traversal lands in phase 5.
    ref: lab 4 ex 1 placeholder.
    """

    queryset = Comment.objects.select_related("author", "post").all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        # parent comment must belong to the same post if provided
        parent = serializer.validated_data.get("parent")
        post = serializer.validated_data.get("post")
        if parent is not None and parent.post_id != post.id:
            raise ValueError("parent comment must belong to the same post")
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        # soft delete keeps the thread structure intact for recursive pruning later
        instance.is_deleted = True
        instance.content = ""
        instance.save(update_fields=["is_deleted", "content"])

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        """ref: lab 4 ex 1 CommentNode.likes. one row per (user, comment)."""
        comment = self.get_object()
        _, created = CommentLike.objects.get_or_create(user=request.user, comment=comment)
        return Response(
            {"liked": True, "like_count": comment.like_count, "created": created},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def unlike(self, request, pk=None):
        comment = self.get_object()
        deleted, _ = CommentLike.objects.filter(user=request.user, comment=comment).delete()
        return Response({"liked": False, "like_count": comment.like_count, "removed": deleted})
