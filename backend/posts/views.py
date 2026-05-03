from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Comment, Like, Post
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
        """
        flat list of top level comments. nested traversal lives in phase 5.
        """
        post = self.get_object()
        top_level = post.comments.filter(parent__isnull=True).select_related("author")
        serializer = CommentSerializer(top_level, many=True, context={"request": request})
        return Response(serializer.data)


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
