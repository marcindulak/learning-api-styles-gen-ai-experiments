from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import WeatherRecord

# FR-004: thresholds that turn a new weather record into a pushed alert.
HEAT_ALERT_THRESHOLD = 35.0
COLD_ALERT_THRESHOLD = -10.0
WIND_ALERT_THRESHOLD = 60.0


def _crossed_alert_types(record):
    # A single reading can cross more than one threshold at once (e.g. a
    # heatwave with high wind); each crossed threshold is reported as its
    # own alert rather than picking one and silently dropping the other.
    alert_types = []
    if record.temperature >= HEAT_ALERT_THRESHOLD:
        alert_types.append("heat")
    if record.temperature <= COLD_ALERT_THRESHOLD:
        alert_types.append("cold")
    if record.wind_speed >= WIND_ALERT_THRESHOLD:
        alert_types.append("wind")
    return alert_types


@receiver(post_save, sender=WeatherRecord)
def send_weather_alerts(sender, instance, created, **kwargs):
    if not created:
        return
    channel_layer = get_channel_layer()
    group_name = f"alerts-{instance.city.uuid}"
    # One group_send per crossed threshold (up to 3) rather than batching
    # them into a single call: no scenario exercises a multi-threshold
    # reading, this isn't a hot path, and batching would change the wire
    # message from one alert object to an array, a bigger consumer-facing
    # change than the rare case it optimizes for (measure before tuning).
    for alert_type in _crossed_alert_types(instance):
        async_to_sync(channel_layer.group_send)(
            group_name,
            {"type": "weather.alert", "alert": {"type": alert_type, "city": instance.city.name}},
        )
