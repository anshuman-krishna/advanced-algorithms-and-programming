from django.contrib import admin

from .models import Category, Hashtag, PostCategory, PostHashtag


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "post_count")
    search_fields = ("name",)


@admin.register(PostHashtag)
class PostHashtagAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "hashtag")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "parent")
    list_filter = ("parent",)


@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "category")
