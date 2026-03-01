"""Weather URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .webhooks import github_webhook
from .feeds import WeatherForecastFeed

router = DefaultRouter(trailing_slash=False)
router.register(r'cities', views.CityViewSet)
router.register(r'weather-records', views.WeatherRecordViewSet)
router.register(r'weather-forecasts', views.WeatherForecastViewSet)
router.register(r'weather-alerts', views.WeatherAlertViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('webhooks/github', github_webhook, name='github_webhook'),
    path('feeds/forecasts', WeatherForecastFeed(), name='forecast_feed'),
]
