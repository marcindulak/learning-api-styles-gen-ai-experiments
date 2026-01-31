"""
WebSocket URL routing for weather alerts.
"""
from django.urls import re_path
from . import consumers


websocket_urlpatterns = [
    re_path(
        r'ws/alerts/(?P<city_uuid>[0-9a-f-]+)$',
        consumers.WeatherAlertConsumer.as_asgi()
    ),
]
