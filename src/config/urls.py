"""Top-level URL configuration."""

from __future__ import annotations

from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path("admin/", admin.site.urls),
    # JWT endpoints. The path "/api/jwt/obtain" is the one prescribed by the
    # REQUIREMENTS.md curl example; "/api/jwt/refresh" is its companion so a
    # client can renew an access token without re-sending credentials.
    path("api/jwt/obtain", TokenObtainPairView.as_view(), name="jwt-obtain"),
    path("api/jwt/refresh", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("api/", include("cities.urls")),
]
