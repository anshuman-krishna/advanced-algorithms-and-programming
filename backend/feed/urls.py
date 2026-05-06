from django.urls import path

from .views import ExploreFeedView, HomeFeedView, TrendingFeedView

urlpatterns = [
    path("home/", HomeFeedView.as_view(), name="feed_home"),
    path("trending/", TrendingFeedView.as_view(), name="feed_trending"),
    path("explore/", ExploreFeedView.as_view(), name="feed_explore"),
]
