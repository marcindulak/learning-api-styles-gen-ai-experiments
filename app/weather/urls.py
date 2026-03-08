"""
URL patterns for weather API.
"""
from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from weather.views import (
    CityViewSet,
    CurrentWeatherViewSet,
    WeatherForecastViewSet,
    fetch_weather_from_api,
    set_test_mode
)

router = DefaultRouter()
router.register(r'cities', CityViewSet, basename='city')
router.register(r'weather/historical', CurrentWeatherViewSet, basename='historical-weather')

urlpatterns = [
    re_path(
        r'^weather/current/(?P<city_name>[^/]+)/$',
        CurrentWeatherViewSet.as_view({'get': 'retrieve'}),
        name='current-weather-detail'
    ),
    re_path(
        r'^weather/forecast/(?P<city_name>[^/]+)/$',
        WeatherForecastViewSet.as_view({'get': 'retrieve'}),
        name='weather-forecast-detail'
    ),
    path(
        'weather/current/',
        CurrentWeatherViewSet.as_view({'post': 'create'}),
        name='current-weather-create'
    ),
    path(
        'weather/forecast/',
        WeatherForecastViewSet.as_view({'post': 'create'}),
        name='weather-forecast-create'
    ),
    path('admin/fetch-weather/', fetch_weather_from_api, name='fetch-weather-api'),
    path('test/set-mode/', set_test_mode, name='set-test-mode'),
    path('', include(router.urls)),
]
