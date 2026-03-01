from django.contrib import admin

from src.weather.models import City


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'region', 'latitude', 'longitude']
    search_fields = ['name', 'country', 'region']
    readonly_fields = ['uuid', 'created_at', 'updated_at']
