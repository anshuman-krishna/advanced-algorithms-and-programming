"""
user model.

ref: claude.md section 4.1 (users entity).
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    bio = models.TextField(blank=True, default="")
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    website = models.URLField(blank=True, default="")
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # btree index on username powers the trie warm path in phase 4
        indexes = [
            models.Index(fields=["username"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.username
