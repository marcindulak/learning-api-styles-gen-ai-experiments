"""Step definitions for FR-005: weather alerts via WebSocket.

Verifies the WebSocket endpoint at ``/ws/alerts`` by driving the ASGI
application in-process through :class:`channels.testing.WebsocketCommunicator`.
This bypasses daphne and the network so the test does not depend on the
live server's process state (e.g. an admin user existing in the dev DB).
The consumer code, channel-layer routing, and ``websocket.http.response``
denial path it exercises are the same in both invocation modes.

Step text reused from other features:

* ``the service is running`` (FR-007's ``fr_007_steps.py``).
"""

from __future__ import annotations

import asyncio
from typing import Any

from behave import given, then, when


def _run(context, coro) -> Any:
    """Run ``coro`` on the per-scenario asyncio loop, creating it on demand.

    A dedicated loop per scenario lets a single WebsocketCommunicator
    instance hold state across Given/When/Then steps without leaking
    futures across scenarios. The loop is closed in
    :func:`_close_loop` once the scenario's WebSocket interactions are done.
    """

    loop = getattr(context, "ws_loop", None)
    if loop is None or loop.is_closed():
        loop = asyncio.new_event_loop()
        context.ws_loop = loop
    return loop.run_until_complete(coro)


def _close_loop(context) -> None:
    loop = getattr(context, "ws_loop", None)
    if loop is not None and not loop.is_closed():
        loop.close()
    context.ws_loop = None


@given('a client is connected to the WebSocket "{path}"')
@when('a client opens a WebSocket connection to "{path}"')
def step_open_websocket(context, path: str) -> None:
    # behave matches steps by (keyword, text). Scenario 1 uses the Given
    # form ("And a client is connected to..." inherits the preceding
    # Given keyword); scenario 2 uses the When form ("When a client
    # opens..."). Two stacked decorators register the same function for
    # both keyword/text combinations.
    from channels.testing import WebsocketCommunicator

    from config.asgi import application

    communicator = WebsocketCommunicator(application, path)
    context.ws_communicator = communicator

    # Drive the handshake manually so the same step handles both an
    # accepted connection (scenario 1) and a 404-denied one (scenario 2)
    # without branching on the path.
    _run(context, communicator.send_input({"type": "websocket.connect"}))
    context.ws_handshake_response = _run(
        context, communicator.receive_output(timeout=5)
    )


@when('an admin publishes a weather alert with text "{text}"')
def step_publish_alert(context, text: str) -> None:
    # Bypassing a hypothetical REST publisher: directly group_send the
    # event the consumer would have received from a real admin POST.
    # The in-memory channel layer is process-local, so this step and the
    # WebsocketCommunicator above share the same layer instance.
    from channels.layers import get_channel_layer

    from cities.consumers import ALERT_EVENT_TYPE, ALERTS_GROUP

    layer = get_channel_layer()
    _run(
        context,
        layer.group_send(
            ALERTS_GROUP,
            {"type": ALERT_EVENT_TYPE, "text": text},
        ),
    )


@then('the connected client receives a message with text "{text}" within {seconds:d} seconds')
def step_receive_alert(context, text: str, seconds: int) -> None:
    # Confirm the handshake succeeded — otherwise receive_from would hang
    # for the whole timeout window with a less helpful error message.
    handshake = context.ws_handshake_response
    assert handshake["type"] == "websocket.accept", (
        f"Expected WebSocket accept, got {handshake!r}."
    )

    received = _run(context, context.ws_communicator.receive_from(timeout=seconds))
    assert received == text, f"Expected {text!r}, got {received!r}."
    _run(context, context.ws_communicator.disconnect())
    _close_loop(context)


@then('the WebSocket handshake fails with HTTP status {status:d}')
def step_handshake_status(context, status: int) -> None:
    msg = context.ws_handshake_response
    assert msg["type"] == "websocket.http.response.start", (
        f"Expected websocket.http.response.start, got {msg!r}."
    )
    assert msg["status"] == status, (
        f"Expected handshake status {status}, got {msg['status']}."
    )
    # Drain the body frame so the communicator exits cleanly.
    _run(context, context.ws_communicator.receive_output(timeout=1))
    _close_loop(context)
