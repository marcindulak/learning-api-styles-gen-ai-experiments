"""WebSocket consumers for the cities app.

FR-005: subscribers connect to ``/ws/alerts`` and receive weather alert
messages broadcast through the channel layer. Connections to any other
path under ``/ws/`` are rejected with HTTP 404 during the WebSocket
handshake.
"""

from __future__ import annotations

from channels.generic.websocket import AsyncWebsocketConsumer


# Group name used by the publishing endpoint (and tests) to fan out an
# alert message to every connected subscriber. Module-level constant so
# the publisher and the consumer cannot drift.
ALERTS_GROUP = "alerts"

# Channel layer event type for an outgoing alert. Channels dispatches the
# event to the consumer method named after the type with dots replaced by
# underscores — here, ``alert_message`` below.
ALERT_EVENT_TYPE = "alert.message"


class AlertsConsumer(AsyncWebsocketConsumer):
    """Subscribe each connected client to the ``alerts`` group."""

    async def connect(self) -> None:
        await self.channel_layer.group_add(ALERTS_GROUP, self.channel_name)
        await self.accept()

    async def disconnect(self, code: int) -> None:
        await self.channel_layer.group_discard(ALERTS_GROUP, self.channel_name)

    async def alert_message(self, event: dict) -> None:
        # ``event`` is the dict passed to ``channel_layer.group_send``; the
        # ``text`` key carries the alert payload the subscriber receives as
        # a WebSocket text frame.
        await self.send(text_data=event["text"])


async def websocket_not_found(scope, receive, send) -> None:
    """Reject WebSocket handshakes with HTTP status 404.

    Uses the ASGI ``websocket.http.response`` extension (Channels 4 /
    daphne 4) so the client sees a real HTTP 404 status rather than a
    plain ``websocket.close`` (which surfaces as 403 or a WebSocket close
    code, not as a 404). The handshake fails before ``accept``, so no
    WebSocket frames are ever exchanged on this connection.
    """

    # Drain the initial ``websocket.connect`` event; without consuming it,
    # the response start below would race against the protocol state.
    await receive()
    await send(
        {
            "type": "websocket.http.response.start",
            "status": 404,
            "headers": [(b"content-type", b"text/plain")],
        }
    )
    await send(
        {
            "type": "websocket.http.response.body",
            "body": b"",
            "more_body": False,
        }
    )
