from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "bio",
            "avatar",
            "website",
            "is_private",
            "follower_count",
            "following_count",
            "post_count",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def get_follower_count(self, obj):
        # ref: lab 6 ex 1, adjacency list size at incoming edges
        return obj.followers.count() if hasattr(obj, "followers") else 0

    def get_following_count(self, obj):
        return obj.following.count() if hasattr(obj, "following") else 0

    def get_post_count(self, obj):
        return obj.posts.count() if hasattr(obj, "posts") else 0


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "token")

    def get_token(self, obj):
        token, _ = Token.objects.get_or_create(user=obj)
        return token.key

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        Token.objects.get_or_create(user=user)
        return user
