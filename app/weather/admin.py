from django.contrib import admin
from .models import City, WeatherRecord, Forecast, WeatherAlert, WebhookEvent


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'region', 'latitude', 'longitude', 'created_at')
    list_filter = ('country', 'region')
    search_fields = ('name', 'country', 'region')
    readonly_fields = ('uuid', 'created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('uuid', 'name', 'country', 'region', 'timezone')
        }),
        ('Coordinates', {
            'fields': ('latitude', 'longitude')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(WeatherRecord)
class WeatherRecordAdmin(admin.ModelAdmin):
    list_display = ('city', 'recorded_at', 'temperature', 'feels_like', 'humidity', 'description')
    list_filter = ('city', 'recorded_at')
    search_fields = ('city__name', 'description')
    readonly_fields = ('uuid',)
    date_hierarchy = 'recorded_at'
    fieldsets = (
        ('Basic Information', {
            'fields': ('uuid', 'city', 'recorded_at', 'description')
        }),
        ('Temperature', {
            'fields': ('temperature', 'feels_like')
        }),
        ('Atmospheric Conditions', {
            'fields': ('humidity', 'pressure', 'precipitation', 'cloud_cover')
        }),
        ('Wind', {
            'fields': ('wind_speed', 'wind_direction')
        }),
        ('Visibility', {
            'fields': ('visibility', 'uv_index')
        }),
    )


@admin.register(Forecast)
class ForecastAdmin(admin.ModelAdmin):
    list_display = ('city', 'forecast_date', 'temperature_high', 'temperature_low', 'humidity', 'description')
    list_filter = ('city', 'forecast_date')
    search_fields = ('city__name', 'description')
    readonly_fields = ('uuid', 'created_at')
    date_hierarchy = 'forecast_date'
    fieldsets = (
        ('Basic Information', {
            'fields': ('uuid', 'city', 'forecast_date', 'description', 'created_at')
        }),
        ('Temperature', {
            'fields': ('temperature_high', 'temperature_low')
        }),
        ('Conditions', {
            'fields': ('humidity', 'wind_speed', 'precipitation_probability')
        }),
    )


@admin.register(WeatherAlert)
class WeatherAlertAdmin(admin.ModelAdmin):
    list_display = ('city', 'alert_type', 'severity', 'title', 'is_active', 'issued_at', 'expires_at')
    list_filter = ('city', 'alert_type', 'severity', 'is_active')
    search_fields = ('city__name', 'title', 'description')
    readonly_fields = ('uuid', 'issued_at')
    date_hierarchy = 'issued_at'
    fieldsets = (
        ('Basic Information', {
            'fields': ('uuid', 'city', 'alert_type', 'severity', 'is_active')
        }),
        ('Details', {
            'fields': ('title', 'description')
        }),
        ('Timing', {
            'fields': ('issued_at', 'expires_at')
        }),
    )


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'received_at', 'processed')
    list_filter = ('event_type', 'processed', 'received_at')
    search_fields = ('event_type', 'payload')
    readonly_fields = ('uuid', 'received_at')
    date_hierarchy = 'received_at'
    fieldsets = (
        ('Basic Information', {
            'fields': ('uuid', 'event_type', 'processed', 'received_at')
        }),
        ('Payload', {
            'fields': ('payload',),
            'classes': ('collapse',)
        }),
    )
