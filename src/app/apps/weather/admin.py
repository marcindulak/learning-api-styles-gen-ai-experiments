from django.contrib import admin
from .models import CurrentWeather


@admin.register(CurrentWeather)
class CurrentWeatherAdmin(admin.ModelAdmin):
    list_display = ('city', 'temperature', 'humidity', 'condition', 'timestamp')
    list_filter = ('city', 'condition_code')
    search_fields = ('city__name', 'condition')
    readonly_fields = ('uuid', 'created_at', 'updated_at')
