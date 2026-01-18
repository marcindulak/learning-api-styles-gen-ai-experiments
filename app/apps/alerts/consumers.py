# WebSocket consumer for weather alerts
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from apps.alerts.models import Alert


class AlertConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for weather alerts."""

    async def connect(self):
        """Handle WebSocket connection."""
        # Get the user from the scope
        user = self.scope.get("user")

        # Check if user is authenticated
        if user is None or isinstance(user, AnonymousUser):
            await self.close(code=4001)  # Custom close code for auth error
            return

        # Accept the connection
        self.user = user
        await self.accept()

        # Add this consumer to the alerts group
        await self.channel_layer.group_add("weather_alerts", self.channel_name)

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Remove this consumer from the alerts group
        if hasattr(self, 'channel_layer'):
            await self.channel_layer.group_discard("weather_alerts", self.channel_name)

    async def receive(self, text_data):
        """Handle incoming messages from the client."""
        try:
            data = json.loads(text_data)

            # Handle different message types
            if data.get('type') == 'alert':
                # Broadcast alert to all connected users
                await self.channel_layer.group_send(
                    "weather_alerts",
                    {
                        "type": "alert.message",
                        "alert_type": data.get('alert_type'),
                        "city": data.get('city'),
                        "description": data.get('description'),
                        "severity": data.get('severity', 'medium'),
                    }
                )
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                "error": "Invalid JSON"
            }))

    async def alert_message(self, event):
        """Handle alert messages sent to this consumer's group."""
        # Send alert message to WebSocket
        await self.send(text_data=json.dumps({
            "type": "alert",
            "alert_type": event.get('alert_type'),
            "city": event.get('city'),
            "description": event.get('description'),
            "severity": event.get('severity'),
        }))

    @database_sync_to_async
    def get_user_alerts(self):
        """Fetch recent alerts for the user."""
        return list(Alert.objects.all()[:10])
