"""URL configuration for the Weather Forecast Service."""
from django.urls import path

from config.views import health

urlpatterns = [
    path("api/health", health, name="health"),
]
