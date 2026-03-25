from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerUIView
from strawberry.django.views import GraphQLView
from weather.schema import schema
from weather.feeds import WeatherForecastFeed

urlpatterns = [
    path("admin/", admin.site.urls),
    # Health check
    path("health/", include("weather.urls_health")),
    # JWT
    path("api/jwt/obtain", TokenObtainPairView.as_view(), name="jwt-obtain"),
    path("api/jwt/refresh", TokenRefreshView.as_view(), name="jwt-refresh"),
    # REST API
    path("api/", include("weather.urls")),
    # GraphQL
    path("graphql/", GraphQLView.as_view(schema=schema)),
    # Atom feed
    path("feed/forecasts/", WeatherForecastFeed(), name="forecast-feed"),
    # OpenAPI
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerUIView.as_view(url_name="schema"), name="swagger-ui"),
]
