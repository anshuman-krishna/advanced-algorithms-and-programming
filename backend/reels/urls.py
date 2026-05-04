from django.urls import path

from .views import (
    ReelsAroundView,
    ReelsMostViewedView,
    ReelsPageView,
    ReelsStatsView,
    ReelsViewedView,
)


urlpatterns = [
    path("page/", ReelsPageView.as_view(), name="reels_page"),
    path("around/<int:post_id>/", ReelsAroundView.as_view(), name="reels_around"),
    path("<int:post_id>/view/", ReelsViewedView.as_view(), name="reels_view"),
    path("most-viewed/", ReelsMostViewedView.as_view(), name="reels_most_viewed"),
    path("stats/", ReelsStatsView.as_view(), name="reels_stats"),
]
