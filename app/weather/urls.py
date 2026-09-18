from django.urls import path

from .views import CurrentWeatherView

urlpatterns = [
    path("cities/<uuid:city_uuid>/current", CurrentWeatherView.as_view(), name="city-current-weather"),
]
