from django.contrib import admin
from .models import WeatherHistory


@admin.register(WeatherHistory)
class WeatherHistoryAdmin(admin.ModelAdmin):
    list_display = ['city', 'date', 'temperature', 'humidity', 'condition']
    list_filter = ['city', 'date']
    search_fields = ['city__name', 'condition']
    ordering = ['-date']
