from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
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
    path("graphql/", csrf_exempt(GraphQLView.as_view(schema=schema))),
    # Atom feed
    path("feed/forecasts/", WeatherForecastFeed(), name="forecast-feed"),
    # OpenAPI
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
