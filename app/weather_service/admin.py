from django.contrib import admin

from weather_service.models import City, WeatherForecast, WeatherRecord


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """Admin interface for City model."""

    list_display = ["name", "country", "region", "timezone", "latitude", "longitude"]
    search_fields = ["name", "country", "region"]
    list_filter = ["country", "region"]
    readonly_fields = ["uuid"]
    ordering = ["name"]


@admin.register(WeatherRecord)
class WeatherRecordAdmin(admin.ModelAdmin):
    """Admin interface for WeatherRecord model."""

    list_display = ["city", "timestamp", "temperature", "humidity", "pressure", "wind_speed", "precipitation"]
    list_filter = ["city", "timestamp"]
    search_fields = ["city__name"]
    readonly_fields = ["timestamp"]
    ordering = ["-timestamp"]
    date_hierarchy = "timestamp"


@admin.register(WeatherForecast)
class WeatherForecastAdmin(admin.ModelAdmin):
    """Admin interface for WeatherForecast model."""

    list_display = ["city", "forecast_date", "temperature", "humidity", "pressure", "created_at"]
    list_filter = ["city", "forecast_date"]
    search_fields = ["city__name"]
    readonly_fields = ["created_at"]
    ordering = ["forecast_date"]
    date_hierarchy = "forecast_date"
