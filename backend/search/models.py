"""
hashtags and explore categories for phase 4.

ref: claude.md section 5.5 (lab 5 generalized trees) for category hierarchy.
ref: claude.md section 5.8 trie for hashtag autocomplete (lab 8 ex 3).
"""

from django.db import models


class Hashtag(models.Model):
    name = models.CharField(max_length=64, unique=True)
    post_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["name"])]

    def __str__(self):
        return f"#{self.name}"


class PostHashtag(models.Model):
    """link table so post text and hashtag entities stay joinable."""

    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE,
                             related_name="hashtag_links")
    hashtag = models.ForeignKey(Hashtag, on_delete=models.CASCADE,
                                related_name="post_links")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["post", "hashtag"],
                                    name="unique_post_hashtag"),
        ]
        indexes = [models.Index(fields=["hashtag", "post"])]


class Category(models.Model):
    """generalized tree node persisted via parent fk."""

    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    parent = models.ForeignKey("self", null=True, blank=True,
                               on_delete=models.CASCADE, related_name="children")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["parent"])]

    def __str__(self):
        return self.name


class PostCategory(models.Model):
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE,
                             related_name="category_links")
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name="post_links")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["post", "category"],
                                    name="unique_post_category"),
        ]
        indexes = [models.Index(fields=["category", "post"])]
