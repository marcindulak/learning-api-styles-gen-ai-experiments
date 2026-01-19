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

        # Extract query parameters
        query_string = self.scope.get('query_string', b'').decode()
        self.query_params = {}
        if query_string:
            for param in query_string.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    self.query_params[key] = value

        # Get city name from query parameters
        self.city_name = self.query_params.get('city', None)

        await self.accept()

        # Add this consumer to the alerts group
        group_name = f"weather_alerts_{self.city_name}" if self.city_name else "weather_alerts"
        await self.channel_layer.group_add(group_name, self.channel_name)
        self.group_name = group_name

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Remove this consumer from the alerts group
        if hasattr(self, 'group_name') and hasattr(self, 'channel_layer'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

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
