"""Steps for the WebSocket alerts API.

The behave-django live server is WSGI-only and cannot upgrade WebSocket
connections, so these steps connect to the real ASGI service on
localhost:8000 (behave runs inside the app container). Alerts published
through the ORM in the test process reach the service's consumers via
the shared redis channel layer, whose messages carry only the alert
payload — no database row crosses the test/real database split.
"""
import json

import parse
import websocket
from behave import given, register_type, then, when

from weather.models import Alert, City

WS_BASE_URL = "ws://localhost:8000"


@parse.with_pattern(r'[^"]*')
def parse_quoted(text):
    return text


register_type(Q=parse_quoted)


def ws_connect(context, path):
    connection = websocket.create_connection(f"{WS_BASE_URL}{path}", timeout=10)
    context.add_cleanup(connection.close)
    # Scenario-scoped log of connected paths, so NFR-003 can replay the
    # handshake against the application container by hostname.
    if not hasattr(context, "ws_paths"):
        context.ws_paths = []
    context.ws_paths.append(path)
    return connection


@given('a client is connected to the WebSocket endpoint "{path:Q}"')
def step_client_connected(context, path):
    context.ws_clients = [ws_connect(context, path)]


@given('{count:d} clients are connected to the WebSocket endpoint "{path:Q}"')
def step_clients_connected(context, count, path):
    context.ws_clients = [ws_connect(context, path) for _ in range(count)]


@when('a client opens a WebSocket connection to "{path:Q}"')
def step_client_opens_connection(context, path):
    context.ws_handshake_error = None
    try:
        context.ws_clients = [ws_connect(context, path)]
    except (websocket.WebSocketException, OSError) as error:
        context.ws_handshake_error = error


@then("the WebSocket handshake succeeds")
def step_handshake_succeeds(context):
    assert context.ws_handshake_error is None, (
        f"WebSocket handshake failed: {context.ws_handshake_error}"
    )
    assert context.ws_clients and context.ws_clients[0].connected, (
        "WebSocket client is not connected"
    )


@when(
    'a weather alert with title "{title:Q}" and severity "{severity:Q}" '
    'is published for the city "{name:Q}"'
)
def step_publish_alert(context, title, severity, name):
    city = City.objects.get(name=name)
    Alert.objects.create(city=city, title=title, severity=severity)


def receive_json_messages(context, seconds):
    messages = []
    for connection in context.ws_clients:
        connection.settimeout(seconds)
        try:
            messages.append(json.loads(connection.recv()))
        except websocket.WebSocketTimeoutException:
            raise AssertionError(
                f"no WebSocket message received within {seconds} seconds"
            )
    context.ws_messages = messages


@then("the connected client receives a JSON message within {seconds:d} seconds")
def step_client_receives_message(context, seconds):
    receive_json_messages(context, seconds)


@then("each connected client receives a JSON message within {seconds:d} seconds")
def step_each_client_receives_message(context, seconds):
    receive_json_messages(context, seconds)


@then('the message contains the field "{field:Q}" with value "{value:Q}"')
def step_message_contains_field(context, field, value):
    message = context.ws_messages[0]
    assert message.get(field) == value, (
        f'expected message field "{field}"="{value}", got: {message}'
    )


@then('each received message contains the field "{field:Q}" with value "{value:Q}"')
def step_each_message_contains_field(context, field, value):
    for message in context.ws_messages:
        assert message.get(field) == value, (
            f'expected message field "{field}"="{value}", got: {message}'
        )
