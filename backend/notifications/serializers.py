from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source="actor.username", read_only=True)

    class Meta:
        model = Notification
        fields = (
            "id",
            "recipient",
            "actor",
            "actor_username",
            "kind",
            "post_id",
            "comment_id",
            "is_priority",
            "is_read",
            "delivered_at",
            "created_at",
        )
        read_only_fields = fields
