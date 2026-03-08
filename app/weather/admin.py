from django.contrib import admin

from .models import City, CurrentWeather, WeatherAlert, WeatherForecast


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'region', 'created_at']
    search_fields = ['name', 'country', 'region']
    list_filter = ['country', 'region']


@admin.register(CurrentWeather)
class CurrentWeatherAdmin(admin.ModelAdmin):
    list_display = ['city', 'temperature', 'humidity', 'timestamp']
    list_filter = ['city', 'timestamp']
    readonly_fields = ['timestamp']


@admin.register(WeatherForecast)
class WeatherForecastAdmin(admin.ModelAdmin):
    list_display = ['city', 'forecast_date', 'temperature', 'humidity']
    list_filter = ['city', 'forecast_date']
    readonly_fields = ['created_at']


@admin.register(WeatherAlert)
class WeatherAlertAdmin(admin.ModelAdmin):
    list_display = ['city', 'severity', 'message', 'timestamp']
    list_filter = ['city', 'severity', 'timestamp']
    readonly_fields = ['timestamp']
