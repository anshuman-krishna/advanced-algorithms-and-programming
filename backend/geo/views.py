"""
geo endpoints over the lab 7 quadtree.

ref: claude.md phase 6.
"""

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services


def _parse_float(raw, default=None):
    try:
        return float(raw)
    except (TypeError, ValueError):
        return default


class GeoNearbyView(APIView):
    """
    GET /api/geo/nearby/?lat=&lng=&radius=&limit=

    radius is in degrees (rough planar units). defaults: radius 1.0, limit 50.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        lat = _parse_float(request.query_params.get("lat"))
        lng = _parse_float(request.query_params.get("lng"))
        if lat is None or lng is None:
            return Response({"detail": "lat and lng are required"}, status=400)
        radius = _parse_float(request.query_params.get("radius"), 1.0)
        limit = int(_parse_float(request.query_params.get("limit"), 50))
        results = services.nearby(lat, lng, radius_deg=radius, limit=limit)
        return Response({
            "lat": lat, "lng": lng, "radius_deg": radius,
            "count": len(results), "results": results,
        })


class GeoBboxView(APIView):
    """
    GET /api/geo/bbox/?min_lat=&min_lng=&max_lat=&max_lng=&limit=
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        params = ["min_lat", "min_lng", "max_lat", "max_lng"]
        values = [_parse_float(request.query_params.get(k)) for k in params]
        if any(v is None for v in values):
            return Response({"detail": "min/max lat and lng are required"}, status=400)
        min_lat, min_lng, max_lat, max_lng = values
        limit = int(_parse_float(request.query_params.get("limit"), 200))
        results = services.bbox(min_lat, min_lng, max_lat, max_lng, limit=limit)
        return Response({
            "bbox": {"min_lat": min_lat, "min_lng": min_lng,
                     "max_lat": max_lat, "max_lng": max_lng},
            "count": len(results), "results": results,
        })


class GeoNearestView(APIView):
    """GET /api/geo/nearest/?lat=&lng=&k="""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        lat = _parse_float(request.query_params.get("lat"))
        lng = _parse_float(request.query_params.get("lng"))
        if lat is None or lng is None:
            return Response({"detail": "lat and lng are required"}, status=400)
        k = int(_parse_float(request.query_params.get("k"), 5))
        results = services.nearest(lat, lng, k=k)
        return Response({"lat": lat, "lng": lng, "k": k, "results": results})


class GeoStatsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(services.stats())

    def post(self, request):
        if request.query_params.get("reset") in ("1", "true"):
            services.force_reset()
        size = services.hydrate_from_db()
        return Response({"hydrated": True, "size": size})
