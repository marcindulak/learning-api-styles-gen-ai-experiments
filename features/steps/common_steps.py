import http.client
import json
import ssl
from typing import NamedTuple
from urllib.parse import urlsplit

from behave import then, when
from django.contrib.auth.models import User
from django.test import Client
from rest_framework_simplejwt.tokens import AccessToken

from weather.providers import OpenMeteoWeatherProvider, WeatherProviderUnavailable, WeatherReading

# The service uses a self-signed certificate for local development (see
# NFR-002), so certificate verification is deliberately disabled here, the
# same trust model curl's own --insecure flag expresses for this same
# self-signed setup.
_UNVERIFIED_TLS_CONTEXT = ssl._create_unverified_context()

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


class _SocketResponse(NamedTuple):
    """Mimics the subset of a Django test-client response the shared
    "a client sends" step needs, for requests that must go over a real
    socket instead of Django's in-process test Client (which never opens
    a TLS connection).
    """

    status_code: int
    tls_version: str | None


def _real_request(method, url):
    parts = urlsplit(url)
    is_https = parts.scheme == "https"
    if is_https:
        connection = http.client.HTTPSConnection(parts.hostname, parts.port, context=_UNVERIFIED_TLS_CONTEXT)
    else:
        connection = http.client.HTTPConnection(parts.hostname, parts.port)
    connection.connect()
    tls_version = connection.sock.version() if is_https else None
    connection.request(method, parts.path or "/")
    response = connection.getresponse()
    response.read()
    connection.close()
    return _SocketResponse(response.status, tls_version)


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
    if "://" in path:
        # Only NFR-002's scenarios use an absolute URL here, to genuinely
        # exercise a real (possibly TLS) socket connection instead of
        # Django's in-process test Client, which never opens one.
        context.last_response = _real_request(method, path)
    else:
        context.last_response = getattr(_client_for(context, "anonymous"), method.lower())(path)


@then("the response status is {status:d}")
def step_then_response_status(context, status):
    assert context.last_response.status_code == status
