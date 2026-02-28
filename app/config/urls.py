"""Root URL configuration for the Weather Forecast Service."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("weather.urls")),
]
