from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """only the author can modify the object."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        author_id = getattr(obj, "author_id", None) or getattr(obj, "user_id", None)
        return author_id == request.user.id
