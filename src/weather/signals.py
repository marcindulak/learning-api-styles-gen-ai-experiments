from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from src.weather.models import WeatherAlert


@receiver(post_save, sender=WeatherAlert)
def broadcast_weather_alert(sender, instance: WeatherAlert, created: bool, **kwargs) -> None:
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'alerts_{instance.city.name}',
            {
                'type': 'alert_message',
                'city': instance.city.name,
                'severity': instance.severity,
                'message': instance.message,
            }
        )
