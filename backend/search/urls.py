from django.urls import path

from .views import (
    CategoryEngagementView,
    ExploreTreeView,
    HashtagAutocompleteView,
    HashtagPostsView,
    HashtagRelatedView,
    IndexStatsView,
    PostSearchView,
    RecommendationsView,
    TrendingHashtagsView,
    UsernameAutocompleteView,
)

urlpatterns = [
    path("posts/", PostSearchView.as_view(), name="search_posts"),
    path("autocomplete/users/", UsernameAutocompleteView.as_view(),
         name="search_autocomplete_users"),
    path("autocomplete/hashtags/", HashtagAutocompleteView.as_view(),
         name="search_autocomplete_hashtags"),
    path("hashtag/<str:name>/posts/", HashtagPostsView.as_view(),
         name="search_hashtag_posts"),
    path("hashtag/<str:name>/related/", HashtagRelatedView.as_view(),
         name="search_hashtag_related"),
    path("hashtags/trending/", TrendingHashtagsView.as_view(),
         name="search_hashtags_trending"),
    path("explore/", ExploreTreeView.as_view(), name="explore_tree"),
    path("explore/<int:category_id>/engagement/",
         CategoryEngagementView.as_view(), name="category_engagement"),
    path("recommendations/", RecommendationsView.as_view(),
         name="search_recommendations"),
    path("stats/", IndexStatsView.as_view(), name="search_stats"),
]
