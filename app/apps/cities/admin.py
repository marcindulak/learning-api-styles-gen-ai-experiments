from django.contrib import admin
from .models import City


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'region', 'timezone', 'uuid')
    list_filter = ('country', 'region')
    search_fields = ('name', 'country')
    readonly_fields = ('uuid', 'created_at', 'updated_at')
    fieldsets = (
        ('Location', {
            'fields': ('name', 'country', 'region', 'latitude', 'longitude')
        }),
        ('Configuration', {
            'fields': ('timezone',)
        }),
        ('Identifiers', {
            'fields': ('uuid',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
