"""Top-level URL configuration."""

from __future__ import annotations

from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from cities.feeds import ForecastFeed


urlpatterns = [
    path("admin/", admin.site.urls),
    # JWT endpoints. The path "/api/jwt/obtain" is the one prescribed by the
    # REQUIREMENTS.md curl example; "/api/jwt/refresh" is its companion so a
    # client can renew an access token without re-sending credentials.
    path("api/jwt/obtain", TokenObtainPairView.as_view(), name="jwt-obtain"),
    path("api/jwt/refresh", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("api/", include("cities.urls")),
    # GitHub posts to /webhooks/github with an HMAC signature; FR-003.
    path("webhooks/", include("webhooks.urls")),
    # Atom 1.0 forecast feed per city; FR-004.
    path(
        "feeds/forecast/<str:name>",
        ForecastFeed(),
        name="city-forecast-feed",
    ),
    # GraphQL endpoint; FR-002. csrf_exempt because GraphQL clients post
    # JSON bodies without a CSRF cookie. graphiql=True exposes the in-browser
    # explorer at the same URL when the request accepts text/html.
    path(
        "graphql",
        csrf_exempt(GraphQLView.as_view(graphiql=True)),
        name="graphql",
    ),
]
