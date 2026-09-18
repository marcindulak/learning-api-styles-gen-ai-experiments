from django.contrib import admin

from .models import City, Forecast, WeatherRecord


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "region")
    search_fields = ("name",)


@admin.register(WeatherRecord)
class WeatherRecordAdmin(admin.ModelAdmin):
    list_display = ("city", "temperature", "recorded_at")
    list_filter = ("city",)


@admin.register(Forecast)
class ForecastAdmin(admin.ModelAdmin):
    list_display = ("city", "date", "condition")
    list_filter = ("city",)
