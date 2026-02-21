"""
Django signals for weather-related events.
Handles broadcasting of weather alerts to WebSocket consumers.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import WeatherAlert


@receiver(post_save, sender=WeatherAlert)
def broadcast_weather_alert(sender, instance, created, **kwargs):
    """
    Signal handler that broadcasts new weather alerts to connected WebSocket clients.
    Uses transaction.on_commit() to ensure broadcast happens AFTER the database
    transaction commits, preventing ghost notifications on rollback.
    """
    if not created:
        # Only broadcast on creation, not on updates
        return

    def broadcast():
        """Broadcast the alert to WebSocket consumers."""
        channel_layer = get_channel_layer()

        # Prepare alert message
        alert_data = {
            'type': 'alert_message',  # This matches the method name in the consumer
            'city': instance.city.name,
            'city_uuid': str(instance.city.uuid),
            'alert_type': instance.alert_type,
            'severity': instance.severity,
            'title': instance.title,
            'description': instance.description,
            'issued_at': instance.issued_at.isoformat(),
        }

        # Broadcast to city-specific group
        async_to_sync(channel_layer.group_send)(
            f'alerts_city_{instance.city.uuid}',
            alert_data
        )

        # Broadcast to general alerts group
        async_to_sync(channel_layer.group_send)(
            'alerts_all',
            alert_data
        )

    # Use transaction.on_commit to ensure broadcast happens AFTER commit
    transaction.on_commit(broadcast)
