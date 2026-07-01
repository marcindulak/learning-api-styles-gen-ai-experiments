"""Steps for HTTP requests and response assertions.

The scenarios run inside the "django-app" container of the compose stack,
so absolute "http://localhost:8000/..." URLs reach the service exactly as
a client on the host does through the published 127.0.0.1:8000 port.
"""
import time

import requests
from behave import given, then, when

SERVICE_ROOT = "http://localhost:8000"


@given("the service is running")
def step_service_is_running(context):
    last_error = None
    for _ in range(30):
        try:
            response = requests.get(f"{SERVICE_ROOT}/api/health", timeout=2)
            if response.status_code == 200:
                return
            last_error = f"status code {response.status_code}"
        except requests.RequestException as exc:
            last_error = str(exc)
        time.sleep(1)
    raise AssertionError(f"service is not running on {SERVICE_ROOT}: {last_error}")


@when('a client sends a GET request to "{url}" from the host')
def step_get_request_from_host(context, url):
    context.response = requests.get(url, timeout=10)


@then("the response status code is {expected:d}")
def step_response_status_code(context, expected):
    actual = context.response.status_code
    assert actual == expected, f"expected status code {expected}, got {actual}"


@then('the response JSON contains the field "{field}" with value "{expected}"')
def step_response_json_field_string(context, field, expected):
    body = context.response.json()
    assert field in body, f'field "{field}" not in response JSON: {body}'
    actual = body[field]
    assert actual == expected, f'expected {field}="{expected}", got "{actual}"'
