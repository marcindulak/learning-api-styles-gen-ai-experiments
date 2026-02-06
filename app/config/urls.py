"""
URL configuration for Weather Forecast Service.
"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from weather_service.views import CityViewSet, WeatherForecastViewSet, WeatherRecordViewSet


def health_check(request):
    return HttpResponse("OK", status=200)


router = DefaultRouter(trailing_slash=False)
router.register(r"cities", CityViewSet, basename="city")
router.register(r"weather-records", WeatherRecordViewSet, basename="weatherrecord")
router.register(r"forecasts", WeatherForecastViewSet, basename="weatherforecast")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", health_check),
    path("api/", include(router.urls)),
    path("api/docs", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/jwt/obtain", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/jwt/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/schema", SpectacularAPIView.as_view(), name="schema"),
]
