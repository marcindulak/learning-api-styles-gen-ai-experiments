import json

from behave import given, then, when
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from common_steps import CITY_DEFAULTS, _auth_header, _client_for

from config.asgi import application
from weather.models import City


@given('"{username}" is authenticated with a JWT obtained from "{path}"')
def step_given_authenticated_with_jwt(context, username, path):
    password = context.user_passwords[username]
    response = _client_for(context, username).post(
        path,
        data=json.dumps({"username": username, "password": password}),
        content_type="application/json",
    )
    assert response.status_code == 200, response.content
    context.jwt_tokens = getattr(context, "jwt_tokens", {})
    context.jwt_tokens[username] = json.loads(response.content)["access"]


@when('"{username}" sends "POST {path}" to create a city named "{city_name}"')
def step_when_creates_city_via_api(context, username, path, city_name):
    context.last_response = _client_for(context, username).post(
        path,
        data=json.dumps({"name": city_name, **CITY_DEFAULTS}),
        content_type="application/json",
        **_auth_header(context, username),
    )


@when('"{username}" sends "{method:w} {path:S}"')
def step_when_named_user_sends_request(context, username, method, path):
    context.last_response = getattr(_client_for(context, username), method.lower())(
        path, **_auth_header(context, username)
    )


@when(
    '"{username}" sends a "POST /api/graphql" query requesting the user profile for username "{target}"'
)
def step_when_graphql_user_profile(context, username, target):
    query = "query($username: String!) { user(username: $username) { username } }"
    context.last_response = _client_for(context, username).post(
        "/api/graphql",
        data=json.dumps({"query": query, "variables": {"username": target}}),
        content_type="application/json",
        **_auth_header(context, username),
    )


async def _ws_connect(name, token):
    city = await database_sync_to_async(City.objects.get)(name=name)
    path = f"/ws/alerts/{city.uuid}/"
    if token:
        path += f"?token={token}"
    communicator = WebsocketCommunicator(application, path)
    connected, _ = await communicator.connect()
    return communicator, connected


def _run_ws_connect(context, name, token):
    communicator, connected = context.ws_loop.run_until_complete(_ws_connect(name, token))
    context.ws_connected = connected
    if connected:
        # Only stores connected communicators for after_scenario to disconnect;
        # per ENTRY 010, disconnecting a never-accepted communicator can crash
        # since the consumer never entered its accept()ed running state.
        context.ws_clients = getattr(context, "ws_clients", {})
        context.ws_clients[f"fr010-{name}"] = communicator


@when('a client attempts to open a WebSocket connection to subscribe to alerts for "{name}" without a JWT')
def step_when_ws_connect_without_jwt(context, name):
    _run_ws_connect(context, name, token=None)


@when('"{username}" opens a WebSocket connection to subscribe to alerts for "{name}" using her own JWT')
def step_when_ws_connect_with_own_jwt(context, username, name):
    _run_ws_connect(context, name, token=context.jwt_tokens[username])


@then("the connection is rejected with an authentication error")
def step_then_ws_connection_rejected(context):
    assert not context.ws_connected


@then("the connection is accepted")
def step_then_ws_connection_accepted(context):
    assert context.ws_connected
