"""Steps that verify the container infrastructure of the service.

The suite executes inside the "django-app" container, so container
liveness is verified through effects observable from within the compose
network, and the compose configuration is read from the read-only mount
of the repository's compose.yaml.
"""
import os
import socket
from urllib.parse import urlsplit, urlunsplit

import parse
import requests
import websocket
import yaml
from behave import given, register_type, then, when

COMPOSE_FILE = "/app/compose.yaml"
DOCKERFILE = "/app/Dockerfile"


@parse.with_pattern(r'[^"]*')
def parse_quoted(text):
    return text


register_type(Q=parse_quoted)


def _container_is_running(name):
    if name == "django-app":
        # This test process runs inside that very container.
        return socket.gethostname() == "django-app"
    # Compose sets hostname == container_name, so a TCP connection to the
    # container's service port proves the container is up.
    ports = {"django-postgres": 5432, "django-redis": 6379}
    try:
        with socket.create_connection((name, ports[name]), timeout=5):
            return True
    except OSError:
        return False


@given('the project provides a "compose.yaml" file at the repository root')
def step_compose_file_exists(context):
    assert os.path.isfile(COMPOSE_FILE), f"{COMPOSE_FILE} is missing"


@when('the stack is started with "docker compose up --detach --wait"')
def step_stack_is_started(context):
    # "docker compose up" is executed on the host before this suite runs;
    # being inside the compose-managed container proves it succeeded.
    hostname = socket.gethostname()
    assert hostname == "django-app", (
        f"expected to run inside the compose stack (hostname django-app), "
        f"got hostname {hostname}"
    )


@then('the container "{name}" is running')
def step_container_is_running(context, name):
    assert _container_is_running(name), f'container "{name}" is not running'


@when("the compose configuration is inspected")
def step_inspect_compose_configuration(context):
    with open(COMPOSE_FILE) as compose_file:
        context.compose = yaml.safe_load(compose_file)


@given('the project provides a "Dockerfile" at the repository root')
def step_dockerfile_exists(context):
    assert os.path.isfile(DOCKERFILE), f"{DOCKERFILE} is missing"


@then("exactly one service builds from the project Dockerfile")
def step_exactly_one_service_builds(context):
    services = context.compose["services"]
    builders = [name for name, service in services.items() if "build" in service]
    assert len(builders) == 1, (
        f"expected exactly one service with a build section, got {builders}"
    )
    build = services[builders[0]]["build"]
    dockerfile = build.get("dockerfile", "Dockerfile")
    assert dockerfile.removeprefix("./") == "Dockerfile", (
        f'service "{builders[0]}" builds from "{dockerfile}", '
        f"not the project Dockerfile"
    )
    context.building_service = builders[0]


@then('that service is named "{name:Q}"')
def step_building_service_is_named(context, name):
    assert context.building_service == name, (
        f'the building service is named "{context.building_service}", not "{name}"'
    )


@then('the "{service:Q}" service uses the image "{image:Q}"')
def step_service_uses_image(context, service, image):
    actual = context.compose["services"][service].get("image")
    assert actual == image, (
        f'service "{service}" uses image "{actual}", expected "{image}"'
    )


def record_http_exchange(context, response):
    # Scenario-scoped log of HTTP exchanges, shared with api_steps.
    if not hasattr(context, "http_exchanges"):
        context.http_exchanges = []
    context.http_exchanges.append(response)


@when(
    'a client sends a POST request to "{url:Q}" '
    "with a valid GraphQL introspection query"
)
def step_post_introspection_query(context, url):
    query = "{ __schema { queryType { name } } }"
    context.response = requests.post(url, json={"query": query}, timeout=10)
    record_http_exchange(context, context.response)


@then("all HTTP responses have status code 200")
def step_all_http_responses_200(context):
    exchanges = getattr(context, "http_exchanges", [])
    assert exchanges, "no HTTP responses were recorded in this scenario"
    for response in exchanges:
        assert response.status_code == 200, (
            f"{response.request.method} {response.url} "
            f"returned {response.status_code}"
        )


def url_on_container(url, container):
    parts = urlsplit(url)
    netloc = f"{container}:{parts.port or 8000}"
    return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))


@then('all endpoints are served by the container "{name:Q}"')
def step_endpoints_served_by_container(context, name):
    # Compose sets hostname == container_name, so replaying every exchange
    # of this scenario against that hostname proves the endpoints are
    # served by that container.
    exchanges = getattr(context, "http_exchanges", [])
    ws_paths = getattr(context, "ws_paths", [])
    assert exchanges or ws_paths, "no endpoints were exercised in this scenario"
    for original in exchanges:
        request = original.request
        headers = {}
        if request.body and "Content-Type" in request.headers:
            headers["Content-Type"] = request.headers["Content-Type"]
        replay = requests.request(
            request.method,
            url_on_container(request.url, name),
            data=request.body,
            headers=headers,
            timeout=10,
        )
        assert replay.status_code == original.status_code, (
            f"{request.method} {request.url} replayed on {name} "
            f"returned {replay.status_code}, expected {original.status_code}"
        )
    for path in ws_paths:
        connection = websocket.create_connection(f"ws://{name}:8000{path}", timeout=10)
        try:
            assert connection.connected, (
                f"WebSocket handshake to ws://{name}:8000{path} failed"
            )
        finally:
            connection.close()


@then('every published port of the "{service}" service is bound to host IP "{ip}"')
def step_published_ports_bound_to_ip(context, service, ip):
    ports = context.compose["services"][service].get("ports", [])
    assert ports, f'service "{service}" publishes no ports'
    for port in ports:
        assert str(port).startswith(f"{ip}:"), (
            f'published port "{port}" of service "{service}" '
            f'is not bound to {ip}'
        )
