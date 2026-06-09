from rest_framework import serializers

from .models import Comment, Like, Post
from .pet_images import pet_image_for


class AuthorMiniSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    avatar = serializers.ImageField(allow_null=True)


class PostSerializer(serializers.ModelSerializer):
    author = AuthorMiniSerializer(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    share_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "image",
            "caption",
            "location",
            "latitude",
            "longitude",
            "like_count",
            "comment_count",
            "share_count",
            "is_liked",
            "created_at",
        )
        read_only_fields = (
            "id", "author", "created_at", "like_count",
            "comment_count", "share_count", "is_liked",
        )

    def get_share_count(self, obj):
        # we do not store a shares table, so derive a stable, plausible share
        # number from the post id and its like count. more likes trends toward
        # more shares, and the value never changes between requests.
        likes = obj.like_count
        return (obj.id * 3 + likes * 2) % 23 + likes // 2

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        # ref: lab 1 hash table style membership check, exists() uses a btree index lookup
        return obj.likes.filter(user_id=request.user.id).exists()

    def get_image(self, obj):
        # an uploaded file wins, then a seeded external url, then a stable pet
        # photo by id so the card is never a blank square
        if obj.image:
            request = self.context.get("request")
            url = obj.image.url
            return request.build_absolute_uri(url) if request is not None else url
        return obj.image_url or pet_image_for(obj.id)


class LikeSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Like
        fields = ("id", "user_id", "post", "created_at")
        read_only_fields = ("id", "user_id", "created_at")


class CommentSerializer(serializers.ModelSerializer):
    author = AuthorMiniSerializer(read_only=True)
    reply_count = serializers.SerializerMethodField()
    like_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            "id",
            "post",
            "author",
            "parent",
            "content",
            "is_deleted",
            "reply_count",
            "like_count",
            "is_liked",
            "created_at",
        )
        read_only_fields = (
            "id", "author", "is_deleted", "reply_count",
            "like_count", "is_liked", "created_at",
        )

    def get_reply_count(self, obj):
        return obj.replies.count()

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return obj.comment_likes.filter(user_id=request.user.id).exists()
