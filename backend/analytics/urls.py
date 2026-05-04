from django.urls import path

from .views import AnalyticsStatsView, LikesRangeView, LikesSeriesView


urlpatterns = [
    path(
        "users/<str:identifier>/likes-range/",
        LikesRangeView.as_view(),
        name="analytics_likes_range",
    ),
    path(
        "users/<str:identifier>/likes-series/",
        LikesSeriesView.as_view(),
        name="analytics_likes_series",
    ),
    path("stats/", AnalyticsStatsView.as_view(), name="analytics_stats"),
]
