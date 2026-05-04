from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/token/", obtain_auth_token, name="api_token_auth"),
    path("api/accounts/", include("accounts.urls")),
    path("api/posts/", include("posts.urls")),
    path("api/social/", include("social.urls")),
    path("api/feed/", include("feed.urls")),
    path("api/search/", include("search.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/reels/", include("reels.urls")),
    path("api/analytics/", include("analytics.urls")),
    path("api/geo/", include("geo.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
