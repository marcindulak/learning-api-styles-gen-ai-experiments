import json

from channels.generic.websocket import AsyncWebsocketConsumer


class AlertConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        self.subscribed_cities = set()
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'welcome',
            'message': 'Connected to weather alerts'
        }))

    async def disconnect(self, close_code: int) -> None:
        for city_name in list(self.subscribed_cities):
            await self.channel_layer.group_discard(
                f'alerts_{city_name}',
                self.channel_name
            )

    async def receive(self, text_data: str) -> None:
        data = json.loads(text_data)
        message_type = data.get('type')
        city_name = data.get('city')

        if message_type == 'subscribe' and city_name:
            await self.channel_layer.group_add(
                f'alerts_{city_name}',
                self.channel_name
            )
            self.subscribed_cities.add(city_name)
            await self.send(text_data=json.dumps({
                'type': 'subscription_confirmed',
                'city': city_name
            }))
        elif message_type == 'unsubscribe' and city_name:
            await self.channel_layer.group_discard(
                f'alerts_{city_name}',
                self.channel_name
            )
            self.subscribed_cities.discard(city_name)
            await self.send(text_data=json.dumps({
                'type': 'unsubscribe_confirmed',
                'city': city_name
            }))

    async def alert_message(self, event: dict) -> None:
        await self.send(text_data=json.dumps({
            'type': 'alert',
            'city': event['city'],
            'severity': event['severity'],
            'message': event['message']
        }))
