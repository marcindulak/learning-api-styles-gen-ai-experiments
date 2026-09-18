import json

from behave import then, when
from django.test import Client

from weather.providers import OpenMeteoWeatherProvider, WeatherProviderUnavailable, WeatherReading

CITY_DEFAULTS = {
    "country": "Testland",
    "region": "Testregion",
    "timezone": "UTC",
    "latitude": 0.0,
    "longitude": 0.0,
}


class FakeWeatherProvider:
    """A hand-written test double substituted for OpenMeteoWeatherProvider.

    Configured directly by Given steps (readings per city, availability),
    then passed into poll_city_weather the same way the real provider would
    be, so no mocking library or monkeypatching is needed.
    """

    name = OpenMeteoWeatherProvider.name

    def __init__(self):
        self.readings = {}
        self.available = True

    def fetch_current(self, city) -> WeatherReading:
        if not self.available:
            raise WeatherProviderUnavailable("fake provider is offline")
        return self.readings[city.name]


def _client_for(context, username):
    context.clients = getattr(context, "clients", {})
    return context.clients.setdefault(username, Client())


def _response_body(context):
    return json.loads(context.last_response.content)


@when('a client sends "{method:w} {path:S}"')
def step_when_sends_request(context, method, path):
    context.last_response = getattr(_client_for(context, "anonymous"), method.lower())(path)


@then("the response status is {status:d}")
def step_then_response_status(context, status):
    assert context.last_response.status_code == status
