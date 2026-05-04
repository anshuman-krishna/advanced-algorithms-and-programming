from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "recipient", "actor", "kind", "is_priority", "is_read", "created_at")
    list_filter = ("kind", "is_priority", "is_read")
    search_fields = ("recipient__username", "actor__username")
