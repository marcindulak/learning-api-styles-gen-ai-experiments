from django.contrib import admin

from .models import City, WeatherRecord


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "region")
    search_fields = ("name",)


@admin.register(WeatherRecord)
class WeatherRecordAdmin(admin.ModelAdmin):
    list_display = ("city", "temperature", "recorded_at")
    list_filter = ("city",)
