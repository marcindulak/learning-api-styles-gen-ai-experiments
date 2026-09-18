from django.urls import path

from .views import CurrentWeatherView, HistoricalWeatherView

urlpatterns = [
    path("cities/<uuid:city_uuid>/current", CurrentWeatherView.as_view(), name="city-current-weather"),
    path("cities/<uuid:city_uuid>/history", HistoricalWeatherView.as_view(), name="city-historical-weather"),
]
