from django.contrib import admin
from .models import WeatherAlert


@admin.register(WeatherAlert)
class WeatherAlertAdmin(admin.ModelAdmin):
    list_display = ('city', 'severity', 'description', 'timestamp')
    list_filter = ('severity', 'city')
    search_fields = ('description', 'city__name')
    ordering = ('-timestamp',)
