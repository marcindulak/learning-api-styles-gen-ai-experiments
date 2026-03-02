from django.contrib import admin

from src.weather.models import City, CurrentWeather, WeatherAlert, WeatherForecast


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'region', 'latitude', 'longitude']
    search_fields = ['name', 'country', 'region']
    readonly_fields = ['uuid', 'created_at', 'updated_at']


@admin.register(CurrentWeather)
class CurrentWeatherAdmin(admin.ModelAdmin):
    list_display = ['city', 'temperature', 'humidity', 'pressure', 'wind_speed', 'conditions', 'timestamp']
    list_filter = ['city', 'timestamp']
    search_fields = ['city__name', 'conditions']
    readonly_fields = ['uuid', 'created_at']


@admin.register(WeatherForecast)
class WeatherForecastAdmin(admin.ModelAdmin):
    list_display = ['city', 'forecast_date', 'temperature', 'humidity', 'pressure', 'wind_speed', 'conditions']
    list_filter = ['city', 'forecast_date']
    search_fields = ['city__name', 'conditions']
    readonly_fields = ['uuid', 'created_at']


@admin.register(WeatherAlert)
class WeatherAlertAdmin(admin.ModelAdmin):
    list_display = ['city', 'severity', 'message', 'created_at']
    list_filter = ['city', 'severity', 'created_at']
    search_fields = ['city__name', 'severity', 'message']
    readonly_fields = ['uuid', 'created_at']
