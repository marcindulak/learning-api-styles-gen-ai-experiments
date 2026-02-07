"""
Step definitions for WebSocket weather alerts feature.
"""
import asyncio
import json

from behave import given, then, when
from channels.testing import WebsocketCommunicator

from config.asgi import application


@given('a client is connected to WebSocket endpoint "{endpoint}"')
def step_connect_websocket(context, endpoint):
    """Connect to WebSocket endpoint."""
    # Use asyncio to run the async connection
    async def connect():
        context.communicator = WebsocketCommunicator(application, endpoint)
        connected, subprotocol = await context.communicator.connect()
        assert connected, f"Failed to connect to WebSocket endpoint {endpoint}"

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(connect())
    context.event_loop = loop


@when('a client connects to WebSocket endpoint "{endpoint}"')
def step_when_connect_websocket(context, endpoint):
    """When step for connecting to WebSocket."""
    step_connect_websocket(context, endpoint)


@then("the WebSocket connection is established")
def step_verify_connection(context):
    """Verify WebSocket connection is established."""
    assert hasattr(
        context, "communicator"
    ), "WebSocket communicator not found in context"
    # Connection is established if we have a communicator
    assert context.communicator is not None, "WebSocket not connected"


@given('the client is subscribed to alerts for city "{city}"')
def step_subscribe_to_city(context, city):
    """Subscribe to alerts for a specific city."""
    async def subscribe():
        await context.communicator.send_json_to({"action": "subscribe", "city": city})
        response = await context.communicator.receive_json_from()
        assert (
            response["type"] == "subscription_confirmation"
        ), f"Expected subscription confirmation, got {response}"
        assert response["city"] == city, f"Expected city {city}, got {response['city']}"

    context.event_loop.run_until_complete(subscribe())


@when('the client sends subscription message for city "{city}"')
def step_when_subscribe_to_city(context, city):
    """When step for sending subscription message."""
    async def subscribe():
        await context.communicator.send_json_to({"action": "subscribe", "city": city})

    context.event_loop.run_until_complete(subscribe())


@then('the client receives confirmation of subscription to "{city}"')
def step_verify_subscription_confirmation(context, city):
    """Verify subscription confirmation message."""
    async def verify():
        response = await context.communicator.receive_json_from()
        assert (
            response["type"] == "subscription_confirmation"
        ), f"Expected subscription confirmation, got {response}"
        assert response["city"] == city, f"Expected city {city}, got {response['city']}"
        assert (
            response["status"] == "subscribed"
        ), f"Expected status 'subscribed', got {response['status']}"

    context.event_loop.run_until_complete(verify())


@when('a weather alert is issued for "{city}" with severity "{severity}"')
def step_issue_weather_alert(context, city, severity):
    """Issue a weather alert for a city."""
    async def send_alert():
        # Send issue_alert action to trigger the alert
        await context.communicator.send_json_to({
            "action": "issue_alert",
            "city": city,
            "severity": severity,
            "message": f"Weather alert for {city}"
        })

    context.event_loop.run_until_complete(send_alert())


@then('the client receives a WebSocket message with alert for "{city}"')
def step_verify_alert_received(context, city):
    """Verify client receives alert message."""
    async def verify():
        response = await context.communicator.receive_json_from()
        assert (
            response["type"] == "weather_alert"
        ), f"Expected weather_alert, got {response}"
        assert response["city"] == city, f"Expected city {city}, got {response['city']}"
        context.last_alert = response

    context.event_loop.run_until_complete(verify())


@then('the alert message contains severity "{severity}"')
def step_verify_alert_severity(context, severity):
    """Verify alert message contains expected severity."""
    assert hasattr(context, "last_alert"), "No alert received"
    assert (
        context.last_alert["severity"] == severity
    ), f"Expected severity {severity}, got {context.last_alert['severity']}"


@when('the client sends unsubscribe message for city "{city}"')
def step_unsubscribe_from_city(context, city):
    """Send unsubscribe message for a city."""
    async def unsubscribe():
        await context.communicator.send_json_to({"action": "unsubscribe", "city": city})

    context.event_loop.run_until_complete(unsubscribe())


@then('the client receives confirmation of unsubscription from "{city}"')
def step_verify_unsubscription_confirmation(context, city):
    """Verify unsubscription confirmation message."""
    async def verify():
        response = await context.communicator.receive_json_from()
        assert (
            response["type"] == "unsubscription_confirmation"
        ), f"Expected unsubscription confirmation, got {response}"
        assert response["city"] == city, f"Expected city {city}, got {response['city']}"
        assert (
            response["status"] == "unsubscribed"
        ), f"Expected status 'unsubscribed', got {response['status']}"

    context.event_loop.run_until_complete(verify())


@when('a weather alert is issued for "{city}"')
def step_issue_alert_without_severity(context, city):
    """Issue a weather alert without specifying severity."""
    async def send_alert():
        await context.communicator.send_json_to({
            "action": "issue_alert",
            "city": city,
            "severity": "medium",
            "message": f"Weather alert for {city}"
        })

    context.event_loop.run_until_complete(send_alert())


@then("the client does not receive the alert message")
def step_verify_no_alert(context):
    """Verify client does not receive alert message."""
    async def verify():
        # Try to receive with timeout - should timeout since no message expected
        try:
            response = await asyncio.wait_for(
                context.communicator.receive_json_from(), timeout=0.5
            )
            # If we get here, we received an unexpected message
            assert False, f"Unexpected message received: {response}"
        except asyncio.TimeoutError:
            # This is expected - no message should be received
            pass

    context.event_loop.run_until_complete(verify())


def after_scenario(context, scenario):
    """Clean up WebSocket connection after each scenario."""
    if hasattr(context, "communicator"):
        async def disconnect():
            await context.communicator.disconnect()

        context.event_loop.run_until_complete(disconnect())
        context.event_loop.close()
