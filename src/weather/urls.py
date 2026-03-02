from django.urls import include, path
from rest_framework.routers import DefaultRouter

from src.weather.views import (
    CityViewSet,
    CurrentWeatherViewSet,
    FetchWeatherView,
    HistoricalWeatherViewSet,
    SetTestModeView,
    WeatherForecastViewSet,
)

router = DefaultRouter()
router.register(r'cities', CityViewSet, basename='city')
router.register(r'weather/current', CurrentWeatherViewSet, basename='current-weather')
router.register(r'weather/historical', HistoricalWeatherViewSet, basename='historical-weather')
router.register(r'weather/forecast', WeatherForecastViewSet, basename='weather-forecast')

urlpatterns = [
    path('', include(router.urls)),
    path('admin/fetch-weather/', FetchWeatherView.as_view(), name='fetch-weather'),
    path('test/set-mode/', SetTestModeView.as_view(), name='set-test-mode'),
]
