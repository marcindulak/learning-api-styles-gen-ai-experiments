from django.contrib import admin
from apps.weather.models import Weather


@admin.register(Weather)
class WeatherAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'city', 'temperature', 'humidity', 'wind_speed', 'timestamp')
    list_filter = ('city', 'timestamp')
    search_fields = ('city__name', 'uuid')
    ordering = ('-timestamp',)
