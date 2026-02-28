"""Signals to broadcast alerts via WebSocket."""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import WeatherAlert


@receiver(post_save, sender=WeatherAlert)
def broadcast_alert(sender, instance, created, **kwargs):
    if not created:
        return

    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    alert_data = {
        "uuid": str(instance.uuid),
        "city": instance.city.name,
        "city_uuid": str(instance.city.uuid),
        "severity": instance.severity,
        "event": instance.event,
        "description": instance.description,
    }

    # Broadcast to the global alerts group
    async_to_sync(channel_layer.group_send)(
        "alerts",
        {"type": "alert.message", "data": alert_data},
    )

    # Also broadcast to city-specific group
    async_to_sync(channel_layer.group_send)(
        f"alerts_{instance.city.uuid}",
        {"type": "alert.message", "data": alert_data},
    )
