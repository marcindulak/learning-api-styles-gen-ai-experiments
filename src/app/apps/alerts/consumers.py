"""
WebSocket consumers for weather alerts.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async


class WeatherAlertConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time weather alerts.
    Clients connect to receive alerts for a specific city.
    """

    async def connect(self):
        """
        Handle WebSocket connection.
        """
        self.city_uuid = self.scope['url_route']['kwargs']['city_uuid']
        self.group_name = f'weather_alerts_{self.city_uuid}'

        # Verify city exists
        city = await self.get_city(self.city_uuid)
        if city is None:
            # City not found, close with error
            await self.close(code=4004)
            return

        # Store city info
        self.city = city

        # Join the city's alert group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Connected to weather alerts for {city["name"]}',
            'city_uuid': self.city_uuid,
            'city_name': city['name'],
        }))

    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        """
        # Leave the alert group
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages.
        Currently, clients don't need to send messages, but this
        could be extended for acknowledgments or subscriptions.
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type', '')

            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                }))
        except json.JSONDecodeError:
            pass

    async def weather_alert(self, event):
        """
        Handle weather alert messages sent to this consumer.
        This is called when a message is sent to the group.
        """
        alert_data = event['alert']

        await self.send(text_data=json.dumps({
            'type': 'weather_alert',
            'alert': alert_data,
        }))

    @database_sync_to_async
    def get_city(self, city_uuid):
        """
        Get city from database by UUID.
        """
        from apps.cities.models import City
        try:
            city = City.objects.get(uuid=city_uuid)
            return {
                'uuid': str(city.uuid),
                'name': city.name,
                'country': city.country,
            }
        except City.DoesNotExist:
            return None


def send_weather_alert(city_uuid, alert_data):
    """
    Helper function to send a weather alert to all connected clients for a city.
    This can be called from views or other parts of the application.
    """
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    channel_layer = get_channel_layer()
    group_name = f'weather_alerts_{city_uuid}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'weather_alert',
            'alert': alert_data,
        }
    )
