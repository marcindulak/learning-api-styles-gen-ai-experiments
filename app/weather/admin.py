"""Django admin configuration for weather models."""
from django.contrib import admin

from .models import City, WeatherAlert, WeatherForecast, WeatherRecord, WebhookEvent


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """City admin configuration."""

    list_display = ['name', 'country', 'region', 'timezone', 'latitude', 'longitude', 'created_at']
    list_filter = ['country', 'region']
    search_fields = ['name', 'country', 'region']
    readonly_fields = ['uuid', 'created_at', 'updated_at']
    ordering = ['name']


@admin.register(WeatherRecord)
class WeatherRecordAdmin(admin.ModelAdmin):
    """Weather record admin configuration."""

    list_display = ['city', 'timestamp', 'temperature', 'humidity', 'weather_condition', 'created_at']
    list_filter = ['city', 'weather_condition', 'timestamp']
    search_fields = ['city__name', 'weather_condition']
    readonly_fields = ['uuid', 'created_at']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'


@admin.register(WeatherForecast)
class WeatherForecastAdmin(admin.ModelAdmin):
    """Weather forecast admin configuration."""

    list_display = ['city', 'forecast_date', 'temperature_min', 'temperature_max', 'weather_condition', 'created_at']
    list_filter = ['city', 'weather_condition', 'forecast_date']
    search_fields = ['city__name', 'weather_condition']
    readonly_fields = ['uuid', 'created_at', 'updated_at']
    ordering = ['forecast_date']
    date_hierarchy = 'forecast_date'


@admin.register(WeatherAlert)
class WeatherAlertAdmin(admin.ModelAdmin):
    """Weather alert admin configuration."""

    list_display = ['city', 'alert_type', 'severity', 'title', 'is_active', 'start_time', 'end_time']
    list_filter = ['severity', 'is_active', 'alert_type', 'city']
    search_fields = ['city__name', 'alert_type', 'title', 'description']
    readonly_fields = ['uuid', 'created_at', 'updated_at']
    ordering = ['-start_time']
    date_hierarchy = 'start_time'


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    """Webhook event admin configuration."""

    list_display = ['event_type', 'delivery_id', 'processed', 'received_at', 'processed_at']
    list_filter = ['processed', 'event_type', 'received_at']
    search_fields = ['event_type', 'delivery_id']
    readonly_fields = ['uuid', 'received_at', 'signature', 'payload']
    ordering = ['-received_at']
    date_hierarchy = 'received_at'
