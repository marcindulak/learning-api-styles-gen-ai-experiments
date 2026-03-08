"""
WebSocket consumers for weather alerts.
"""
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class AlertConsumer(WebsocketConsumer):
    """WebSocket consumer for weather alerts."""

    def connect(self):
        """Accept WebSocket connection."""
        self.subscribed_cities = set()
        self.accept()

    def disconnect(self, close_code):
        """Leave all city groups on disconnect."""
        for city_name in self.subscribed_cities:
            async_to_sync(self.channel_layer.group_discard)(
                f'alerts_{city_name}',
                self.channel_name
            )

    def receive(self, text_data):
        """Handle messages from WebSocket."""
        data = json.loads(text_data)
        action = data.get('action')
        city_name = data.get('city')

        if action == 'subscribe' and city_name:
            self.subscribed_cities.add(city_name)
            async_to_sync(self.channel_layer.group_add)(
                f'alerts_{city_name}',
                self.channel_name
            )
            self.send(text_data=json.dumps({
                'type': 'confirmation',
                'message': f'Subscribed to {city_name}'
            }))

        elif action == 'unsubscribe' and city_name:
            if city_name in self.subscribed_cities:
                self.subscribed_cities.remove(city_name)
                async_to_sync(self.channel_layer.group_discard)(
                    f'alerts_{city_name}',
                    self.channel_name
                )
                self.send(text_data=json.dumps({
                    'type': 'confirmation',
                    'message': f'Unsubscribed from {city_name}'
                }))

    def alert_message(self, event):
        """Send alert to WebSocket."""
        self.send(text_data=json.dumps({
            'type': 'alert',
            'city': event['city'],
            'severity': event['severity'],
            'message': event['message']
        }))
