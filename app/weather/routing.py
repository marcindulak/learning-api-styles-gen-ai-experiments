"""
WebSocket URL routing for Django Channels.
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # General alerts endpoint
    re_path(r'ws/alerts/$', consumers.WeatherAlertConsumer.as_asgi()),
    # Per-city alerts endpoint
    re_path(r'ws/alerts/(?P<city_uuid>[a-f0-9\-]+)/$', consumers.WeatherAlertConsumer.as_asgi()),
]
