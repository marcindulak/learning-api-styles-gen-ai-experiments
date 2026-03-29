from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"cities", views.CityViewSet, basename="city")
router.register(r"records", views.WeatherRecordViewSet, basename="weatherrecord")
router.register(r"forecasts", views.WeatherForecastViewSet, basename="weatherforecast")
router.register(r"alerts", views.WeatherAlertViewSet, basename="weatheralert")

urlpatterns = [
    path("", include(router.urls)),
    path("webhooks/github/", views.GitHubWebhookView.as_view(), name="github-webhook"),
]
