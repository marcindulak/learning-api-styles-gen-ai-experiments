from rest_framework import serializers
from .models import WebhookEvent


class WebhookEventSerializer(serializers.ModelSerializer):
    """
    Serializer for WebhookEvent model.
    """
    class Meta:
        model = WebhookEvent
        fields = ['uuid', 'event_type', 'delivery_id', 'payload', 'received_at']
        read_only_fields = ['uuid', 'received_at']
