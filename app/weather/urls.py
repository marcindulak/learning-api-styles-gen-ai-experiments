"""
URL patterns for weather API.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from weather.views import CityViewSet, CurrentWeatherViewSet, WeatherForecastViewSet

router = DefaultRouter()
router.register(r'cities', CityViewSet, basename='city')
router.register(r'weather/current', CurrentWeatherViewSet, basename='current-weather')
router.register(r'weather/forecast', WeatherForecastViewSet, basename='weather-forecast')
router.register(r'weather/historical', CurrentWeatherViewSet, basename='historical-weather')

urlpatterns = [
    path('', include(router.urls)),
]
