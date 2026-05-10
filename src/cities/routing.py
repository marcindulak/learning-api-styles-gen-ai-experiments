"""WebSocket URL routing for the cities app (FR-005).

Mounted by ``config.asgi.application`` under the top-level ``URLRouter``.
The catch-all entry at the end maps every unmatched WebSocket path to a
404 denier so a client connecting to ``/ws/unknown`` receives an HTTP 404
during the handshake rather than a generic close.
"""

from __future__ import annotations

from django.urls import re_path

from cities.consumers import AlertsConsumer, websocket_not_found


websocket_urlpatterns = [
    re_path(r"^ws/alerts$", AlertsConsumer.as_asgi()),
    # The trailing catch-all must stay last; URLRouter consults entries in
    # order and the first match wins.
    re_path(r"^.*$", websocket_not_found),
]
