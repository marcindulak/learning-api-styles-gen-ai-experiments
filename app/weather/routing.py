"""WebSocket URL routing."""

from django.urls import path

from .consumers import AlertConsumer

websocket_urlpatterns = [
    path("ws/alerts", AlertConsumer.as_asgi()),
]
