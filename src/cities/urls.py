"""URL routes for the cities app."""

from __future__ import annotations

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CityViewSet
from .weather import current_weather, forecast, history


# trailing_slash=False so REQUIREMENTS.md's curl examples
# (e.g. ``GET /api/cities``) match the routes verbatim.
router = DefaultRouter(trailing_slash=False)
router.register("cities", CityViewSet, basename="city")

urlpatterns = router.urls + [
    path(
        "cities/<str:name>/weather/current",
        current_weather,
        name="city-weather-current",
    ),
    path(
        "cities/<str:name>/weather/forecast",
        forecast,
        name="city-weather-forecast",
    ),
    path(
        "cities/<str:name>/weather/history",
        history,
        name="city-weather-history",
    ),
]
