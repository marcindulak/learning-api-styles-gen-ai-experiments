"""WebSocket consumers for weather alerts."""

import asyncio
import json

from channels.generic.websocket import AsyncWebSocketConsumer


class AlertConsumer(AsyncWebSocketConsumer):
    async def connect(self):
        self.subscribed_city = None
        await self.channel_layer.group_add("alerts", self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({"type": "connection_established"}))
        self._ping_task = asyncio.ensure_future(self._ping_loop())

    async def disconnect(self, close_code):
        if hasattr(self, "_ping_task"):
            self._ping_task.cancel()
        await self.channel_layer.group_discard("alerts", self.channel_name)
        if self.subscribed_city:
            await self.channel_layer.group_discard(
                f"alerts_{self.subscribed_city}", self.channel_name
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        if data.get("type") == "subscribe" and "city_uuid" in data:
            city_uuid = data["city_uuid"]
            if self.subscribed_city:
                await self.channel_layer.group_discard(
                    f"alerts_{self.subscribed_city}", self.channel_name
                )
            self.subscribed_city = city_uuid
            await self.channel_layer.group_add(
                f"alerts_{city_uuid}", self.channel_name
            )

    async def alert_message(self, event):
        """Handle alert broadcast from signal."""
        alert_data = event["data"]
        # If subscribed to a specific city, only forward matching alerts
        if self.subscribed_city and alert_data.get("city_uuid") != self.subscribed_city:
            return
        await self.send(
            text_data=json.dumps({"type": "alert", "data": alert_data})
        )

    async def _ping_loop(self):
        try:
            while True:
                await asyncio.sleep(60)
                await self.send(text_data=json.dumps({"type": "ping"}))
        except asyncio.CancelledError:
            pass
