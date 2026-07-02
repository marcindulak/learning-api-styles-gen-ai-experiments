"""Publishing of weather alerts to WebSocket clients.

Alerts are broadcast through the channel layer (redis), so every process
holding consumers subscribed to the alerts group delivers the message to
its connected WebSocket clients.
"""
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

ALERTS_GROUP = "alerts"


def publish_alert(alert):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        ALERTS_GROUP,
        {
            "type": "alert.message",
            "alert": {
                "title": alert.title,
                "severity": alert.severity,
                "city": alert.city.name,
            },
        },
    )
