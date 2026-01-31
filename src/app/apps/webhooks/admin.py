from django.contrib import admin
from .models import WebhookEvent


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'event_type', 'delivery_id', 'received_at']
    list_filter = ['event_type', 'received_at']
    search_fields = ['delivery_id', 'event_type']
    readonly_fields = ['uuid', 'received_at']
