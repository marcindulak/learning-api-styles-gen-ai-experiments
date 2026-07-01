"""Steps that verify the container infrastructure of the service.

The suite executes inside the "django-app" container, so container
liveness is verified through effects observable from within the compose
network, and the compose configuration is read from the read-only mount
of the repository's compose.yaml.
"""
import os
import socket

import yaml
from behave import given, then, when

COMPOSE_FILE = "/app/compose.yaml"


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


@then('every published port of the "{service}" service is bound to host IP "{ip}"')
def step_published_ports_bound_to_ip(context, service, ip):
    ports = context.compose["services"][service].get("ports", [])
    assert ports, f'service "{service}" publishes no ports'
    for port in ports:
        assert str(port).startswith(f"{ip}:"), (
            f'published port "{port}" of service "{service}" '
            f'is not bound to {ip}'
        )
