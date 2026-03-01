from django.urls import include, path
from rest_framework.routers import DefaultRouter

from src.weather.views import (
    CityViewSet,
    CurrentWeatherViewSet,
    HistoricalWeatherViewSet,
    WeatherForecastViewSet,
)

router = DefaultRouter()
router.register(r'cities', CityViewSet, basename='city')
router.register(r'weather/current', CurrentWeatherViewSet, basename='current-weather')
router.register(r'weather/historical', HistoricalWeatherViewSet, basename='historical-weather')
router.register(r'weather/forecast', WeatherForecastViewSet, basename='weather-forecast')

urlpatterns = [
    path('', include(router.urls)),
]
