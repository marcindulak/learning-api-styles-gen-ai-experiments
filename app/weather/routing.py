"""WebSocket URL routing."""
from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/alerts', consumers.WeatherAlertConsumer.as_asgi()),
]
