"""Admin-site (CMS) registrations for the weather domain models."""
from django.contrib import admin

from weather.models import Alert, City, ForecastRecord, WeatherRecord


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "region", "timezone")
    search_fields = ("name", "country")


@admin.register(WeatherRecord)
class WeatherRecordAdmin(admin.ModelAdmin):
    list_display = ("city", "observed_at", "temperature", "source")
    list_filter = ("city",)


@admin.register(ForecastRecord)
class ForecastRecordAdmin(admin.ModelAdmin):
    list_display = ("city", "forecast_date", "temperature_min", "temperature_max")
    list_filter = ("city",)


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("title", "severity", "city", "created_at")
    list_filter = ("severity", "city")
