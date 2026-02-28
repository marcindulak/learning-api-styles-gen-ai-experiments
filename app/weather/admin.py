"""Admin site configuration for the Weather Forecast Service."""

from django.contrib import admin

from .models import City, WeatherAlert, WeatherForecast, WeatherRecord


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "region")
    search_fields = ("name",)
    list_filter = ("region",)


@admin.register(WeatherRecord)
class WeatherRecordAdmin(admin.ModelAdmin):
    list_display = ("city", "timestamp", "temperature")
    list_filter = ("city", "timestamp")


@admin.register(WeatherForecast)
class WeatherForecastAdmin(admin.ModelAdmin):
    list_display = ("city", "forecast_date", "temperature_high", "temperature_low")
    list_filter = ("city",)


@admin.register(WeatherAlert)
class WeatherAlertAdmin(admin.ModelAdmin):
    list_display = ("city", "severity", "event", "active")
    list_filter = ("severity", "active")
