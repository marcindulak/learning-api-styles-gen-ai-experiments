from django.urls import include, path
from rest_framework.routers import DefaultRouter

from src.weather.views import (
    AsyncAPISchemaView,
    CityViewSet,
    CurrentWeatherViewSet,
    FetchWeatherView,
    HistoricalWeatherViewSet,
    SetEnvironmentView,
    SetTestModeView,
    WeatherAlertViewSet,
    WeatherForecastViewSet,
)

router = DefaultRouter()
router.register(r'cities', CityViewSet, basename='city')
router.register(r'weather/alerts', WeatherAlertViewSet, basename='weather-alert')
router.register(r'weather/current', CurrentWeatherViewSet, basename='current-weather')
router.register(r'weather/historical', HistoricalWeatherViewSet, basename='historical-weather')
router.register(r'weather/forecast', WeatherForecastViewSet, basename='weather-forecast')

urlpatterns = [
    path('', include(router.urls)),
    path('admin/fetch-weather/', FetchWeatherView.as_view(), name='fetch-weather'),
    path('asyncapi-schema/', AsyncAPISchemaView.as_view(), name='asyncapi-schema'),
    path('test/set-mode/', SetTestModeView.as_view(), name='set-test-mode'),
    path('test/set-env/', SetEnvironmentView.as_view(), name='set-environment'),
]
