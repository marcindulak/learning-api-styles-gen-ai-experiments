"""WebSocket consumers for weather alerts."""
import json

from channels.generic.websocket import AsyncWebsocketConsumer


class WeatherAlertConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for weather alerts."""

    async def connect(self) -> None:
        """Handle WebSocket connection."""
        self.group_name = 'weather_alerts'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to weather alerts'
        }))

    async def disconnect(self, close_code: int) -> None:
        """Handle WebSocket disconnection."""
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data: str) -> None:
        """Handle messages from WebSocket."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'unknown')

            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'message': 'pong'
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))

    async def weather_alert(self, event: dict) -> None:
        """Handle weather alert broadcast."""
        await self.send(text_data=json.dumps({
            'type': 'weather_alert',
            'alert': event['alert']
        }))
