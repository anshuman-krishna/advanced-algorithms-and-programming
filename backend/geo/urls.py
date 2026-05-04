from django.urls import path

from .views import GeoBboxView, GeoNearbyView, GeoNearestView, GeoStatsView


urlpatterns = [
    path("nearby/", GeoNearbyView.as_view(), name="geo_nearby"),
    path("bbox/", GeoBboxView.as_view(), name="geo_bbox"),
    path("nearest/", GeoNearestView.as_view(), name="geo_nearest"),
    path("stats/", GeoStatsView.as_view(), name="geo_stats"),
]
