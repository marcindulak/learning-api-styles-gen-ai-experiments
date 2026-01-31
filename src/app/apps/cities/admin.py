from django.contrib import admin
from .models import City


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'region', 'timezone', 'latitude', 'longitude')
    search_fields = ('name', 'country', 'region')
    list_filter = ('country', 'region')
    readonly_fields = ('uuid', 'created_at', 'updated_at')
