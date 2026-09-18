import json

from channels.generic.websocket import AsyncWebsocketConsumer


class AlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        city_uuid = self.scope["url_route"]["kwargs"]["city_uuid"]
        self.group_name = f"alerts-{city_uuid}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def weather_alert(self, event):
        await self.send(text_data=json.dumps(event["alert"]))
