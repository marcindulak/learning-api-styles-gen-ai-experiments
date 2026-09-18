import json

from behave import then, when
from django.test import Client

CITY_DEFAULTS = {
    "country": "Testland",
    "region": "Testregion",
    "timezone": "UTC",
    "latitude": 0.0,
    "longitude": 0.0,
}


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
