"""Step definitions for WebSocket weather alerts feature."""

import json
import subprocess
import time

import django
from behave import given, then, when

django.setup()

from src.weather.models import City, WeatherAlert

import websocket


@when('I connect to WebSocket "{endpoint}"')
def step_connect_websocket(context, endpoint):
    """Connect to a WebSocket endpoint."""
    context.ws = websocket.WebSocket()
    context.ws.connect(f'ws://localhost:8000{endpoint}')


@then('the WebSocket connection is established')
def step_websocket_connected(context):
    """Verify WebSocket connection is established."""
    assert context.ws.connected, "WebSocket is not connected"


@then('I receive a welcome message')
def step_receive_welcome_message(context):
    """Verify welcome message is received."""
    message = context.ws.recv()
    data = json.loads(message)
    assert data['type'] == 'welcome', f"Expected welcome message, got: {data}"


@given('I am connected to WebSocket "{endpoint}"')
def step_given_connected_websocket(context, endpoint):
    """Ensure connected to WebSocket endpoint."""
    step_connect_websocket(context, endpoint)
    step_websocket_connected(context)
    step_receive_welcome_message(context)


@when('I send a subscribe message for city "{city_name}"')
def step_send_subscribe_message(context, city_name):
    """Send a subscribe message for a city."""
    message = json.dumps({
        'type': 'subscribe',
        'city': city_name
    })
    context.ws.send(message)


@then('I receive a subscription confirmation for "{city_name}"')
def step_receive_subscription_confirmation(context, city_name):
    """Verify subscription confirmation is received."""
    message = context.ws.recv()
    data = json.loads(message)
    assert data['type'] == 'subscription_confirmed', f"Expected subscription confirmation, got: {data}"
    assert data['city'] == city_name, f"Expected city {city_name}, got: {data['city']}"


@given('I am subscribed to alerts for "{city_name}"')
def step_given_subscribed(context, city_name):
    """Ensure subscribed to alerts for a city."""
    step_send_subscribe_message(context, city_name)
    step_receive_subscription_confirmation(context, city_name)


@when('a weather alert is created for "{city_name}" with severity "{severity}" and message "{message_text}"')
def step_create_weather_alert(context, city_name, severity, message_text):
    """Create a weather alert for a city via API."""
    payload = json.dumps({
        "city_name": city_name,
        "severity": severity,
        "message": message_text
    })
    subprocess.run(
        [
            'curl',
            '--data', payload,
            '--header', 'Content-Type: application/json',
            '--request', 'POST',
            '--silent',
            'http://localhost:8000/api/weather/alerts/'
        ],
        capture_output=True,
        timeout=10
    )
    time.sleep(0.5)


@then('I receive an alert message for "{city_name}"')
def step_receive_alert_message(context, city_name):
    """Verify alert message is received."""
    message = context.ws.recv()
    data = json.loads(message)
    assert data['type'] == 'alert', f"Expected alert message, got: {data}"
    assert data['city'] == city_name, f"Expected city {city_name}, got: {data['city']}"
    context.last_alert = data


@then('the alert contains field "{field}" with value "{value}"')
def step_alert_contains_field(context, field, value):
    """Verify alert contains a specific field with value."""
    assert field in context.last_alert, f"Field {field} not found in alert: {context.last_alert}"
    assert context.last_alert[field] == value, \
        f"Expected {field}={value}, got: {context.last_alert[field]}"


@when('I send an unsubscribe message for city "{city_name}"')
def step_send_unsubscribe_message(context, city_name):
    """Send an unsubscribe message for a city."""
    message = json.dumps({
        'type': 'unsubscribe',
        'city': city_name
    })
    context.ws.send(message)


@then('I receive an unsubscribe confirmation for "{city_name}"')
def step_receive_unsubscribe_confirmation(context, city_name):
    """Verify unsubscribe confirmation is received."""
    message = context.ws.recv()
    data = json.loads(message)
    assert data['type'] == 'unsubscribe_confirmed', f"Expected unsubscribe confirmation, got: {data}"
    assert data['city'] == city_name, f"Expected city {city_name}, got: {data['city']}"


@then('I do not receive alerts for "{city_name}"')
def step_do_not_receive_alerts(context, city_name):
    """Verify no alerts are received after unsubscribing."""
    payload = json.dumps({
        "city_name": city_name,
        "severity": "low",
        "message": "Test alert after unsubscribe"
    })
    subprocess.run(
        [
            'curl',
            '--data', payload,
            '--header', 'Content-Type: application/json',
            '--request', 'POST',
            '--silent',
            'http://localhost:8000/api/weather/alerts/'
        ],
        capture_output=True,
        timeout=10
    )
    time.sleep(0.5)
    context.ws.settimeout(1)
    try:
        message = context.ws.recv()
        assert False, f"Should not receive alerts after unsubscribing, got: {message}"
    except websocket.WebSocketTimeoutException:
        pass


@given('client "{client_id}" is connected and subscribed to "{city_name}"')
def step_client_connected_subscribed(context, client_id, city_name):
    """Create a client connection and subscribe to city."""
    if not hasattr(context, 'ws_clients'):
        context.ws_clients = {}

    ws = websocket.WebSocket()
    ws.connect('ws://localhost:8000/ws/alerts')
    ws.recv()

    message = json.dumps({
        'type': 'subscribe',
        'city': city_name
    })
    ws.send(message)
    ws.recv()

    context.ws_clients[client_id] = ws


@then('client "{client_id}" receives the alert')
def step_client_receives_alert(context, client_id):
    """Verify a specific client receives the alert."""
    ws = context.ws_clients[client_id]
    message = ws.recv()
    data = json.loads(message)
    assert data['type'] == 'alert', f"Expected alert message, got: {data}"
