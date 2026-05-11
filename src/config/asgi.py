"""ASGI entry point for the Weather Forecast Service.

Used by daphne (the dev/production ASGI server) and by Channels' WebSocket
routing for the weather-alerts channel (FR-005). HTTP traffic still goes
through Django's standard HTTP handler; WebSocket connections are routed
through the ``URLRouter`` below.
"""

from __future__ import annotations

import os

import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Importing channels and the consumer module must happen AFTER django.setup()
# so the Django app registry is populated; channels reads it during routing.
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from django.core.asgi import get_asgi_application  # noqa: E402

from cities.routing import websocket_urlpatterns  # noqa: E402


application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": URLRouter(websocket_urlpatterns),
    }
)
