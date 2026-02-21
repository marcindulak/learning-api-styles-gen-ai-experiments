"""
WebSocket consumers for real-time weather alerts using Django Channels.
"""
import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class WeatherAlertConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for weather alerts.
    Supports two endpoints:
    - ws://localhost:8001/ws/alerts/ (general alerts from all cities)
    - ws://localhost:8001/ws/alerts/<city_uuid>/ (alerts for specific city)
    """

    async def connect(self):
        """Handle WebSocket connection."""
        # Extract city_uuid from URL if provided
        self.city_uuid = self.scope['url_route']['kwargs'].get('city_uuid')

        # Determine group name based on whether city_uuid is specified
        if self.city_uuid:
            self.group_name = f'alerts_city_{self.city_uuid}'
        else:
            self.group_name = 'alerts_all'

        # Join the group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave the group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def alert_message(self, event):
        """
        Handle alert messages sent to the group.
        This method receives messages from the group_send call.
        """
        # Send the alert to the WebSocket
        await self.send_json({
            'type': 'alert',
            'city': event['city'],
            'city_uuid': event['city_uuid'],
            'alert_type': event['alert_type'],
            'severity': event['severity'],
            'title': event['title'],
            'description': event['description'],
            'issued_at': event['issued_at'],
        })

    async def receive_json(self, content):
        """
        Handle incoming JSON messages from the client.
        Currently just acknowledges ping messages for connection testing.
        """
        if content.get('type') == 'ping':
            await self.send_json({'type': 'pong'})
