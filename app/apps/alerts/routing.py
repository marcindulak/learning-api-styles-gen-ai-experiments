# WebSocket routing for alerts
from django.urls import re_path
from apps.alerts.consumers import AlertConsumer

websocket_urlpatterns = [
    re_path(r'ws/alerts/$', AlertConsumer.as_asgi()),
]
