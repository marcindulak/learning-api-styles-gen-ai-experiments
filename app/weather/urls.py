from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CityViewSet, WeatherRecordViewSet, ForecastViewSet
from .feeds import AllCityForecastFeed, CityForecastFeed
from .webhooks import github_webhook

router = DefaultRouter()
router.register(r'cities', CityViewSet, basename='city')
router.register(r'weather-records', WeatherRecordViewSet, basename='weather-record')
router.register(r'forecasts', ForecastViewSet, basename='forecast')

urlpatterns = [
    path('', include(router.urls)),
    # Atom feeds
    path('feeds/forecasts/', AllCityForecastFeed(), name='feed_all_forecasts'),
    path('feeds/forecasts/<uuid:city_uuid>/', CityForecastFeed(), name='feed_city_forecasts'),
    # GitHub webhooks
    path('webhooks/github/', github_webhook, name='github_webhook'),
]
