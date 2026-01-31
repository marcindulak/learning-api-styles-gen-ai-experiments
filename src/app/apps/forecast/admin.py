from django.contrib import admin
from .models import WeatherForecast


@admin.register(WeatherForecast)
class WeatherForecastAdmin(admin.ModelAdmin):
    list_display = ['city', 'forecast_date', 'temperature', 'condition']
    list_filter = ['city', 'forecast_date']
    search_fields = ['city__name', 'condition']
