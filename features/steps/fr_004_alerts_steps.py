import json

from behave import given, then, when
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from common_steps import FakeWeatherProvider, _jwt_for

from config.asgi import application
from weather.models import City
from weather.providers import WeatherReading
from weather.services import poll_city_weather


def _provider(context):
    if not hasattr(context, "weather_provider"):
        context.weather_provider = FakeWeatherProvider()
    return context.weather_provider


def _trigger_reading(context, name, temperature, wind_speed):
    provider = _provider(context)
    provider.readings[name] = WeatherReading(
        temperature=temperature,
        humidity=50,
        wind_speed=wind_speed,
        precipitation_probability=0,
        condition="Clear",
    )
    poll_city_weather(City.objects.get(name=name), provider)


async def _connect(context, name, token):
    city = await database_sync_to_async(City.objects.get)(name=name)
    communicator = WebsocketCommunicator(application, f"/ws/alerts/{city.uuid}/?token={token}")
    connected, _ = await communicator.connect()
    assert connected
    context.ws_clients[name] = communicator


@given('a client has an open WebSocket connection subscribed to alerts for "{name}"')
def step_given_subscribed_client(context, name):
    context.ws_clients = getattr(context, "ws_clients", {})
    token = _jwt_for("_fr004_ws_client")
    context.ws_loop.run_until_complete(_connect(context, name, token))


@when('"{name}" receives a new weather record with temperature {temperature:g}')
def step_when_new_record_temperature(context, name, temperature):
    context.ws_loop.run_until_complete(
        database_sync_to_async(_trigger_reading)(context, name, temperature, 10.0)
    )


@when('"{name}" receives a new weather record with wind_speed {wind_speed:g}')
def step_when_new_record_wind(context, name, wind_speed):
    context.ws_loop.run_until_complete(
        database_sync_to_async(_trigger_reading)(context, name, 20.0, wind_speed)
    )


@when('"{name}" receives a new weather record with temperature {temperature:g} and wind_speed {wind_speed:g}')
def step_when_new_record_both(context, name, temperature, wind_speed):
    context.ws_loop.run_until_complete(
        database_sync_to_async(_trigger_reading)(context, name, temperature, wind_speed)
    )


@then('the subscribed client receives an alert message with type "{alert_type}" and city "{name}"')
def step_then_receives_alert(context, alert_type, name):
    message = context.ws_loop.run_until_complete(context.ws_clients[name].receive_from())
    assert json.loads(message) == {"type": alert_type, "city": name}


@then("the subscribed client receives no alert message")
def step_then_receives_no_alert(context):
    # The Background always opens exactly one subscribed connection; scenarios
    # that also subscribe a second city use the "the client subscribed to ..."
    # wording below instead, so referring to "the" single client is unambiguous.
    (communicator,) = context.ws_clients.values()
    assert context.ws_loop.run_until_complete(communicator.receive_nothing())


@then('the client subscribed to "{name}" receives no alert message')
def step_then_named_receives_no_alert(context, name):
    assert context.ws_loop.run_until_complete(context.ws_clients[name].receive_nothing())
