"""
WebSocket routing configuration for weather_service.
"""
from django.urls import path

from .consumers import WeatherAlertConsumer

websocket_urlpatterns = [
    path("ws/alerts", WeatherAlertConsumer.as_asgi()),
]
