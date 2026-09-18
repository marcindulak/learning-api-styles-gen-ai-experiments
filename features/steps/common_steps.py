import json

from behave import then, when
from django.contrib.auth.models import User
from django.test import Client
from rest_framework_simplejwt.tokens import AccessToken

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


def _jwt_for(username, is_staff=False):
    # FR-010 made JWT auth mandatory for city-creation and WebSocket-alert
    # requests; other features' scenarios never named a specific user for
    # those requests, so this fixture user/token exists only to satisfy that
    # requirement without changing those features' own Gherkin text.
    user, _ = User.objects.get_or_create(username=username, defaults={"is_staff": is_staff})
    return str(AccessToken.for_user(user))


def _auth_header(context, username):
    token = getattr(context, "jwt_tokens", {}).get(username)
    if token is None:
        return {}
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


@when('a client sends "{method:w} {path:S}"')
def step_when_sends_request(context, method, path):
    context.last_response = getattr(_client_for(context, "anonymous"), method.lower())(path)


@then("the response status is {status:d}")
def step_then_response_status(context, status):
    assert context.last_response.status_code == status
