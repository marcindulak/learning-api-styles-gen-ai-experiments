from django.urls import path

from .feeds import ForecastAtomFeed
from .views import (
    CityListCreateView,
    CurrentWeatherView,
    ForecastView,
    HistoricalWeatherView,
    UserDetailView,
)

urlpatterns = [
    path("cities", CityListCreateView.as_view(), name="city-list-create"),
    path("cities/<uuid:city_uuid>/current", CurrentWeatherView.as_view(), name="city-current-weather"),
    path("cities/<uuid:city_uuid>/history", HistoricalWeatherView.as_view(), name="city-historical-weather"),
    path("cities/<uuid:city_uuid>/forecast", ForecastView.as_view(), name="city-forecast"),
    path("cities/<uuid:city_uuid>/forecast/feed.atom", ForecastAtomFeed(), name="city-forecast-feed"),
    path("users/<str:username>", UserDetailView.as_view(), name="user-detail"),
]
