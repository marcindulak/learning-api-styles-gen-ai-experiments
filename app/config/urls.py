"""
URL configuration for Weather Forecast Service.
"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path


def health_check(request):
    return HttpResponse("OK", status=200)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", health_check),
]
