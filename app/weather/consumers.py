"""WebSocket consumers of the Weather Forecast Service."""
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from weather.alerts import ALERTS_GROUP


class AlertsConsumer(AsyncJsonWebsocketConsumer):
    """Broadcasts published weather alerts to all connected clients."""

    async def connect(self):
        await self.channel_layer.group_add(ALERTS_GROUP, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(ALERTS_GROUP, self.channel_name)

    async def alert_message(self, event):
        await self.send_json(event["alert"])
