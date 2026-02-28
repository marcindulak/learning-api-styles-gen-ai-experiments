"""URL configuration for the weather API."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from strawberry.django.views import GraphQLView

from .feeds import ForecastAtomFeed
from .schema import schema
from .views import (
    CityViewSet,
    WeatherAlertViewSet,
    WeatherForecastViewSet,
    WeatherRecordViewSet,
    github_webhook,
    health_check,
)

router = DefaultRouter(trailing_slash=False)
router.register(r"cities", CityViewSet, basename="city")
router.register(r"alerts", WeatherAlertViewSet, basename="alert")

city_weather_list = WeatherRecordViewSet.as_view({"get": "list", "post": "create"})
city_weather_detail = WeatherRecordViewSet.as_view({"get": "retrieve"})
city_forecast_list = WeatherForecastViewSet.as_view({"get": "list", "post": "create"})

urlpatterns = [
    path("jwt/obtain", TokenObtainPairView.as_view(), name="token_obtain"),
    path("jwt/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("health", health_check, name="health_check"),
    path("webhooks/github", github_webhook, name="github_webhook"),
    path("feed/forecasts", ForecastAtomFeed(), name="forecast_feed"),
    path(
        "graphql",
        GraphQLView.as_view(schema=schema),
        name="graphql",
    ),
    path(
        "cities/<uuid:city_uuid>/weather",
        city_weather_list,
        name="city-weather-list",
    ),
    path(
        "cities/<uuid:city_uuid>/weather/<uuid:uuid>",
        city_weather_detail,
        name="city-weather-detail",
    ),
    path(
        "cities/<uuid:city_uuid>/forecast",
        city_forecast_list,
        name="city-forecast-list",
    ),
    path("", include(router.urls)),
]
