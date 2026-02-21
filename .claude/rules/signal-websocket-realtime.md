# Signal-Based WebSocket Real-Time Updates

Django signals trigger WebSocket broadcasts for real-time notifications without explicit coupling between models and consumers.

## The Pattern

**Models (app/weather/models.py):**
```python
class WeatherAlert(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

**Signal Handler (app/weather/signals.py):**
```python
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=WeatherAlert)
def broadcast_weather_alert(sender, instance, created, **kwargs):
    """Broadcast new weather alert to WebSocket subscribers."""
    if created:
        # Broadcast to Channels layer
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'weather_alerts',
            {
                'type': 'weather_alert_message',
                'data': {
                    'city_uuid': str(instance.city.uuid),
                    'severity': instance.severity,
                    'message': instance.message,
                }
            }
        )

# Register signals in apps.py
# In weather/apps.py:
def ready(self):
    import weather.signals  # noqa: F401
```

**WebSocket Consumer (app/weather/consumers.py):**
```python
from channels.generic.websocket import AsyncWebsocketConsumer

class AlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add('weather_alerts', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('weather_alerts', self.channel_name)

    async def weather_alert_message(self, event):
        """Receive message from group and send to WebSocket."""
        await self.send(text_data=json.dumps(event['data']))
```

## Why This Pattern

- **Decoupling:** Models don't import consumer code — signals provide the connection
- **Reusability:** Same signal can broadcast to multiple consumer groups
- **Testability:** Signal handlers are pure functions (easy to mock)
- **Non-blocking:** Uses `async_to_sync` to call async channel layer from sync signal handler

## Common Mistakes

- **Forgetting to register signals** — Signal won't fire if not imported in `apps.py` `ready()` method
- **Blocking operations in signal handler** — Don't do database queries in signals; they run synchronously
- **Missing channel layer group management** — Consumers must join/leave groups in `connect()`/`disconnect()`

## Examples

**Good:**

```python
# Signal handler is pure, calls channel layer
@receiver(post_save, sender=WeatherAlert)
def broadcast_alert(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'weather_alerts',
            {'type': 'weather_alert_message', 'data': {...}}
        )

# Consumer joins group on connect
async def connect(self):
    await self.channel_layer.group_add('weather_alerts', self.channel_name)
    await self.accept()
```

**Bad:**

```python
# Don't do complex DB queries in signals
@receiver(post_save, sender=WeatherAlert)
def broadcast_alert(sender, instance, created, **kwargs):
    # ❌ Blocking, slows down model save
    all_alerts = WeatherAlert.objects.filter(severity='critical').count()
    # This will block the entire request/signal chain

# Don't forget to import signals
# ❌ Missing from apps.py ready() — signal never fires
```

## Integration Points

- Signal handler imports `get_channel_layer` from `channels.layers`
- Uses `async_to_sync()` from `asgiref.sync` to bridge sync signal → async channel layer
- Consumer must be registered in `app/weather/routing.py` and ASGI config
- WebSocket URL pattern in `app/config/urls.py` routes to consumer via `ProtocolTypeRouter`
