from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    FollowViewSet,
    GraphStatsView,
    RelationshipView,
    SuggestionsView,
    UserGraphView,
)

router = DefaultRouter()
router.register(r"follows", FollowViewSet, basename="follow")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "users/<str:identifier>/<str:kind>/",
        UserGraphView.as_view(),
        name="user_graph",
    ),
    path(
        "relationship/<str:identifier>/<str:other>/",
        RelationshipView.as_view(),
        name="relationship",
    ),
    path("suggestions/", SuggestionsView.as_view(), name="suggestions"),
    path("graph/stats/", GraphStatsView.as_view(), name="graph_stats"),
]
