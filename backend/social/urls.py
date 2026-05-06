from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CommunitiesView,
    CommunityOfView,
    FollowViewSet,
    GraphStatsView,
    NichePostsView,
    ReachView,
    RelationshipView,
    ShortestChainView,
    SuggestionsView,
    UserGraphView,
)

router = DefaultRouter()
router.register(r"follows", FollowViewSet, basename="follow")

urlpatterns = [
    path("", include(router.urls)),
    # specific routes must come before the wildcard <str:kind> below
    path("communities/", CommunitiesView.as_view(), name="communities"),
    path("shortest-chain/", ShortestChainView.as_view(), name="shortest_chain"),
    path("suggestions/", SuggestionsView.as_view(), name="suggestions"),
    path("graph/stats/", GraphStatsView.as_view(), name="graph_stats"),
    path(
        "users/<str:identifier>/community/",
        CommunityOfView.as_view(),
        name="community_of",
    ),
    path(
        "users/<str:identifier>/niche-posts/",
        NichePostsView.as_view(),
        name="niche_posts",
    ),
    path(
        "users/<str:identifier>/reach/",
        ReachView.as_view(),
        name="reach",
    ),
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
]
