"""
Step definitions for Feature 010: WebSocket Weather Alerts

This module uses Django Channels' testing utilities with proper event loop management.
"""
import json
import asyncio
from behave import given, when, then
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async


def get_websocket_application():
    """Get the ASGI application for WebSocket testing."""
    from config.asgi import application
    return application


def get_event_loop(context):
    """Get or create a shared event loop for the test context."""
    if not hasattr(context, '_ws_event_loop') or context._ws_event_loop is None or context._ws_event_loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        context._ws_event_loop = loop
    return context._ws_event_loop


def run_async(context, coro):
    """Run an async coroutine using the shared event loop."""
    loop = get_event_loop(context)
    return loop.run_until_complete(coro)


async def async_connect_websocket(city_uuid):
    """Async helper to connect to WebSocket and get initial message."""
    application = get_websocket_application()
    communicator = WebsocketCommunicator(
        application,
        f"/ws/alerts/{city_uuid}"
    )

    connected, close_code = await communicator.connect()

    message = None
    if connected:
        try:
            message = await asyncio.wait_for(
                communicator.receive_json_from(),
                timeout=3.0
            )
        except asyncio.TimeoutError:
            message = None
        except Exception:
            message = None

    return communicator, connected, close_code, message


async def async_disconnect(communicator):
    """Async helper to disconnect from WebSocket."""
    await communicator.disconnect()


async def async_receive_message(communicator, timeout=3.0):
    """Async helper to receive a message."""
    try:
        return await asyncio.wait_for(
            communicator.receive_json_from(),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        return None


async def async_send_group_message(city_uuid, alert_data):
    """Send a message to the WebSocket group."""
    from channels.layers import get_channel_layer
    channel_layer = get_channel_layer()
    group_name = f'weather_alerts_{city_uuid}'

    await channel_layer.group_send(
        group_name,
        {
            'type': 'weather_alert',
            'alert': alert_data,
        }
    )


@when('I connect to the WebSocket alerts endpoint for city "{city_name}"')
def step_connect_websocket(context, city_name):
    """Connect to the WebSocket alerts endpoint for a city."""
    assert hasattr(context, 'city_uuids') and city_name in context.city_uuids, \
        f"City UUID for '{city_name}' not found"

    city_uuid = context.city_uuids[city_name]
    context.websocket_city_uuid = city_uuid
    context.websocket_city_name = city_name

    # Connect using async helper
    communicator, connected, close_code, message = run_async(
        context,
        async_connect_websocket(str(city_uuid))
    )

    context.websocket_connected = connected
    context.websocket_close_code = close_code
    context.websocket_communicator = communicator
    context.websocket_message = message


@when('I connect to the WebSocket alerts endpoint for non-existent city UUID "{city_uuid}"')
def step_connect_websocket_nonexistent(context, city_uuid):
    """Try to connect to WebSocket for a non-existent city."""
    context.websocket_city_uuid = city_uuid

    # Connect using async helper
    communicator, connected, close_code, message = run_async(
        context,
        async_connect_websocket(city_uuid)
    )

    context.websocket_connected = connected
    context.websocket_close_code = close_code
    context.websocket_communicator = communicator

    if not connected:
        context.websocket_error = "Connection rejected for invalid city"


@then('the WebSocket connection is established successfully')
def step_websocket_connected(context):
    """Verify the WebSocket connection was established."""
    assert context.websocket_connected is True, \
        "WebSocket connection was not established"


@then('I receive a connection confirmation message')
def step_receive_confirmation(context):
    """Verify a connection confirmation message was received."""
    message = context.websocket_message
    assert message is not None, "No message received"
    assert message.get('type') == 'connection_established', \
        f"Expected 'connection_established' message, got: {message}"
    assert 'city_uuid' in message, "Message should contain city_uuid"
    assert 'city_name' in message, "Message should contain city_name"


@given('I am connected to the WebSocket alerts endpoint for city "{city_name}"')
def step_already_connected_websocket(context, city_name):
    """Ensure we're connected to the WebSocket endpoint."""
    # First make sure city exists
    if not hasattr(context, 'city_uuids') or city_name not in context.city_uuids:
        # Create the city
        from features.steps.city_steps import step_city_exists
        step_city_exists(context, city_name)

    # Connect
    step_connect_websocket(context, city_name)

    # Verify connection
    assert context.websocket_connected is True, \
        f"Failed to connect to WebSocket for city {city_name}"


@when('a weather alert is triggered for city "{city_name}"')
def step_trigger_alert(context, city_name):
    """Trigger a weather alert for the city."""
    assert hasattr(context, 'city_uuids') and city_name in context.city_uuids, \
        f"City UUID for '{city_name}' not found"

    city_uuid = context.city_uuids[city_name]

    # Create alert in database
    from apps.alerts.models import WeatherAlert
    from apps.cities.models import City

    city = City.objects.get(uuid=city_uuid)
    alert = WeatherAlert.objects.create(
        city=city,
        severity='high',
        description='Severe thunderstorm warning in effect',
    )

    context.triggered_alert = alert

    # Send alert via channels using async helper with shared event loop
    run_async(context, async_send_group_message(str(city_uuid), alert.to_dict()))

    # Give the consumer a moment to process
    import time
    time.sleep(0.1)


@then('I receive a WebSocket message containing the alert')
def step_receive_alert_message(context):
    """Verify we received a WebSocket message with the alert."""
    assert hasattr(context, 'websocket_communicator'), \
        "No WebSocket communicator available"

    message = run_async(context, async_receive_message(context.websocket_communicator, timeout=3.0))

    if message is None:
        raise AssertionError("Failed to receive alert message: timeout")

    context.received_alert_message = message

    assert message.get('type') == 'weather_alert', \
        f"Expected 'weather_alert' message type, got: {message}"
    assert 'alert' in message, f"Message should contain 'alert' key: {message}"


@then('the alert contains severity level')
def step_alert_has_severity(context):
    """Verify the alert contains severity level."""
    message = context.received_alert_message
    alert = message.get('alert', {})
    assert 'severity' in alert, f"Alert should contain 'severity': {alert}"
    assert alert['severity'] in ['low', 'moderate', 'high', 'severe', 'extreme'], \
        f"Invalid severity level: {alert['severity']}"


@then('the alert contains alert description')
def step_alert_has_description(context):
    """Verify the alert contains a description."""
    message = context.received_alert_message
    alert = message.get('alert', {})
    assert 'description' in alert, f"Alert should contain 'description': {alert}"
    assert len(alert['description']) > 0, "Alert description should not be empty"


@then('the alert contains timestamp')
def step_alert_has_timestamp(context):
    """Verify the alert contains a timestamp."""
    message = context.received_alert_message
    alert = message.get('alert', {})
    assert 'timestamp' in alert, f"Alert should contain 'timestamp': {alert}"


@then('the alert contains city UUID')
def step_alert_has_city_uuid(context):
    """Verify the alert contains city UUID."""
    message = context.received_alert_message
    alert = message.get('alert', {})
    assert 'city_uuid' in alert, f"Alert should contain 'city_uuid': {alert}"


@then('the alert contains city name')
def step_alert_has_city_name(context):
    """Verify the alert contains city name."""
    message = context.received_alert_message
    alert = message.get('alert', {})
    assert 'city_name' in alert, f"Alert should contain 'city_name': {alert}"


@when('I close the WebSocket connection')
def step_close_websocket(context):
    """Close the WebSocket connection."""
    assert hasattr(context, 'websocket_communicator'), \
        "No WebSocket communicator available"

    run_async(context, async_disconnect(context.websocket_communicator))
    context.websocket_disconnected = True


@then('the WebSocket connection is closed successfully')
def step_websocket_closed(context):
    """Verify the WebSocket connection was closed."""
    assert context.websocket_disconnected is True, \
        "WebSocket was not disconnected"


@then('the WebSocket connection is rejected')
def step_websocket_rejected(context):
    """Verify the WebSocket connection was rejected."""
    assert context.websocket_connected is False, \
        f"Expected WebSocket to be rejected, but it connected"


@then('I receive an error message about invalid city')
def step_receive_error_invalid_city(context):
    """Verify we received an error message about invalid city."""
    # For rejected connections, the close code indicates the error
    # We use 4004 to indicate city not found
    assert hasattr(context, 'websocket_close_code') or hasattr(context, 'websocket_error'), \
        "No error information available"

    # Either we have a close code or connection was rejected
    if hasattr(context, 'websocket_close_code'):
        # 4004 is our custom code for city not found
        assert context.websocket_close_code == 4004, \
            f"Expected close code 4004, got {context.websocket_close_code}"
