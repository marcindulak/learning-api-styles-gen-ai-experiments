from django.contrib import admin
from .models import City, WeatherRecord, WeatherForecast, WeatherAlert


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "region", "latitude", "longitude")
    search_fields = ("name", "country", "region")
    readonly_fields = ("uuid", "created_at", "updated_at")


@admin.register(WeatherRecord)
class WeatherRecordAdmin(admin.ModelAdmin):
    list_display = ("city", "recorded_at", "temperature_celsius", "humidity_percent", "wind_speed_kmh")
    list_filter = ("city",)
    search_fields = ("city__name",)
    readonly_fields = ("uuid", "created_at")
    ordering = ("-recorded_at",)


@admin.register(WeatherForecast)
class WeatherForecastAdmin(admin.ModelAdmin):
    list_display = ("city", "forecast_date", "temperature_max_celsius", "temperature_min_celsius")
    list_filter = ("city",)
    search_fields = ("city__name",)
    readonly_fields = ("uuid", "created_at", "updated_at")


@admin.register(WeatherAlert)
class WeatherAlertAdmin(admin.ModelAdmin):
    list_display = ("city", "severity", "title", "issued_at", "expires_at")
    list_filter = ("city", "severity")
    search_fields = ("title", "message", "city__name")
    readonly_fields = ("uuid",)
