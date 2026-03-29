import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.urls import re_path


class WeatherAlertConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for live weather alerts per city."""

    async def connect(self):
        self.city_uuid = self.scope["url_route"]["kwargs"]["city_uuid"]
        self.group_name = f"alerts_{self.city_uuid}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({
            "type": "connected",
            "city_uuid": self.city_uuid,
            "message": f"Subscribed to alerts for city {self.city_uuid}",
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return
        if data.get("type") == "ping":
            await self.send(text_data=json.dumps({"type": "pong"}))

    async def alert_message(self, event):
        """Receive alert from channel layer and forward to WebSocket client."""
        await self.send(text_data=json.dumps({
            "type": "alert",
            "uuid": event["uuid"],
            "city": event["city"],
            "severity": event["severity"],
            "title": event["title"],
            "message": event["message"],
            "issued_at": event["issued_at"],
        }))


websocket_urlpatterns = [
    re_path(r"ws/alerts/(?P<city_uuid>[0-9a-f-]+)/$", WeatherAlertConsumer.as_asgi()),
]
