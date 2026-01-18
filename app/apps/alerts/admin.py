from django.contrib import admin
from apps.alerts.models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('alert_type', 'city', 'severity', 'created_at')
    list_filter = ('alert_type', 'severity', 'created_at')
    search_fields = ('city__name', 'description')
    readonly_fields = ('created_at', 'updated_at')
