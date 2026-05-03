from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("id", "username", "email", "is_private", "created_at")
    search_fields = ("username", "email")
    fieldsets = UserAdmin.fieldsets + (
        ("profile", {"fields": ("bio", "avatar", "website", "is_private")}),
    )
