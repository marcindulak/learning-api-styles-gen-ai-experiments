"""WebSocket URL routing of the Weather Forecast Service."""
from django.urls import path

from weather.consumers import AlertsConsumer

websocket_urlpatterns = [
    path("ws/alerts", AlertsConsumer.as_asgi(), name="ws-alerts"),
]
