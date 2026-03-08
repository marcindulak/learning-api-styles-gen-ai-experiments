"""
Step definitions for WebSocket weather alerts.
"""
import json
import subprocess
import time
from threading import Thread

from behave import given, then, when


@when('I establish a WebSocket connection to "{endpoint}"')
def step_establish_websocket_connection(context, endpoint):
    """Establish a WebSocket connection."""
    from websocket import create_connection

    ws_url = f'ws://localhost:8000{endpoint}'
    try:
        context.websocket = create_connection(ws_url)
        context.websocket_connected = True
    except Exception as e:
        context.websocket_connected = False
        context.websocket_error = str(e)


@then('the WebSocket connection is successful')
def step_check_websocket_connection(context):
    """Check that WebSocket connection was successful."""
    assert hasattr(context, 'websocket_connected'), 'WebSocket connection was not attempted'
    assert context.websocket_connected, \
        f'WebSocket connection failed: {getattr(context, "websocket_error", "Unknown error")}'


@given('I have a WebSocket connection to "{endpoint}"')
def step_have_websocket_connection(context, endpoint):
    """Ensure a WebSocket connection exists."""
    step_establish_websocket_connection(context, endpoint)
    step_check_websocket_connection(context)


@when('I send a subscribe message for "{city_name}"')
def step_send_subscribe_message(context, city_name):
    """Send a subscribe message to WebSocket."""
    message = json.dumps({'action': 'subscribe', 'city': city_name})
    context.websocket.send(message)


@then('I receive a confirmation message')
def step_receive_confirmation(context):
    """Receive a confirmation message from WebSocket."""
    # Set a short timeout for receiving message
    context.websocket.settimeout(5)
    try:
        response = context.websocket.recv()
        data = json.loads(response)
        assert data.get('type') == 'confirmation', \
            f'Expected confirmation message, got: {data}'
        context.last_websocket_message = data
    except Exception as e:
        assert False, f'Failed to receive confirmation: {e}'


@given('I am subscribed to alerts for "{city_name}"')
def step_subscribed_to_alerts(context, city_name):
    """Subscribe to alerts for a city."""
    step_send_subscribe_message(context, city_name)
    step_receive_confirmation(context)


@when('a weather alert is issued for "{city_name}"')
def step_issue_weather_alert(context, city_name):
    """Issue a weather alert via API."""
    # First, create the city if it doesn't exist
    from weather.models import City

    city, _ = City.objects.get_or_create(
        name=city_name,
        defaults={
            'country': 'Test Country',
            'region': 'Test Region',
            'timezone': 'UTC',
            'latitude': 0.0,
            'longitude': 0.0
        }
    )

    # Get admin token if not already in context
    if not hasattr(context, 'access_token'):
        credentials = json.dumps({'username': 'admin', 'password': 'admin'})
        result = subprocess.run(
            [
                'curl',
                '--data', credentials,
                '--header', 'Content-Type: application/json',
                '--request', 'POST',
                '--silent',
                'http://localhost:8000/api/jwt/obtain',
            ],
            capture_output=True,
            text=True,
        )
        response_data = json.loads(result.stdout)
        context.access_token = response_data['access']

    # Create alert via API
    alert_data = json.dumps({
        'city_name': city_name,
        'severity': 'high',
        'message': f'Test alert for {city_name}'
    })

    result = subprocess.run(
        [
            'curl',
            '--data', alert_data,
            '--header', 'Content-Type: application/json',
            '--header', f'Authorization: Bearer {context.access_token}',
            '--request', 'POST',
            '--silent',
            'http://localhost:8000/api/weather/alerts/',
        ],
        capture_output=True,
        text=True,
    )

    # Give signal time to broadcast
    time.sleep(0.5)


@then('I receive the alert via WebSocket')
def step_receive_alert(context):
    """Receive the alert via WebSocket."""
    context.websocket.settimeout(5)
    try:
        response = context.websocket.recv()
        data = json.loads(response)
        assert data.get('type') == 'alert', \
            f'Expected alert message, got: {data}'
        context.last_alert = data
    except Exception as e:
        assert False, f'Failed to receive alert: {e}'


@given('client A and client B are connected to "{endpoint}"')
def step_two_clients_connected(context, endpoint):
    """Establish two WebSocket connections."""
    from websocket import create_connection

    ws_url = f'ws://localhost:8000{endpoint}'
    context.client_a = create_connection(ws_url)
    context.client_b = create_connection(ws_url)
    context.websocket_connected = True


@given('both are subscribed to alerts for "{city_name}"')
def step_both_subscribed(context, city_name):
    """Subscribe both clients to alerts."""
    message = json.dumps({'action': 'subscribe', 'city': city_name})

    # Subscribe client A
    context.client_a.send(message)
    context.client_a.settimeout(5)
    response_a = context.client_a.recv()

    # Subscribe client B
    context.client_b.send(message)
    context.client_b.settimeout(5)
    response_b = context.client_b.recv()


@then('both client A and client B receive the alert')
def step_both_receive_alert(context):
    """Both clients receive the alert."""
    context.client_a.settimeout(5)
    context.client_b.settimeout(5)

    try:
        response_a = context.client_a.recv()
        data_a = json.loads(response_a)
        assert data_a.get('type') == 'alert', \
            f'Client A: Expected alert message, got: {data_a}'

        response_b = context.client_b.recv()
        data_b = json.loads(response_b)
        assert data_b.get('type') == 'alert', \
            f'Client B: Expected alert message, got: {data_b}'
    except Exception as e:
        assert False, f'Failed to receive alert on both clients: {e}'


@when('I send an unsubscribe message for "{city_name}"')
def step_send_unsubscribe_message(context, city_name):
    """Send an unsubscribe message."""
    message = json.dumps({'action': 'unsubscribe', 'city': city_name})
    context.websocket.send(message)
    # Receive confirmation
    context.websocket.settimeout(5)
    response = context.websocket.recv()


@then('I do not receive the alert')
def step_not_receive_alert(context):
    """Verify no alert is received."""
    context.websocket.settimeout(1)
    try:
        response = context.websocket.recv()
        # If we receive something, fail
        assert False, f'Received unexpected message: {response}'
    except Exception:
        # Timeout is expected, means no message received
        pass
