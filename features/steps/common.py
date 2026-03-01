"""Common step definitions used across multiple features."""

import json
import subprocess

from behave import given, then, when


@given('the service is running')
def step_service_is_running(context):
    """Verify that the Django service is running and accessible."""
    result = subprocess.run(
        ['curl', '--fail', '--silent', 'http://localhost:8000/'],
        capture_output=True,
        timeout=5
    )
    # Service should respond (even if 404, connection is working)
    assert result.returncode in [0, 22], "Service is not accessible"


@when('I send a POST request to "{endpoint}" with credentials "{username}" and "{password}"')
def step_post_credentials(context, endpoint, username, password):
    """Send a POST request with username and password credentials."""
    payload = json.dumps({"username": username, "password": password})
    result = subprocess.run(
        [
            'curl',
            '--data', payload,
            '--header', 'Content-Type: application/json',
            '--request', 'POST',
            '--silent',
            '--write-out', '\\n%{http_code}',
            f'http://localhost:8000{endpoint}'
        ],
        capture_output=True,
        text=True,
        timeout=10
    )

    lines = result.stdout.strip().split('\n')
    context.response_status_code = int(lines[-1])
    context.response_body = '\n'.join(lines[:-1]) if len(lines) > 1 else ''

    try:
        context.response_json = json.loads(context.response_body) if context.response_body else {}
    except json.JSONDecodeError:
        context.response_json = {}


@then('the response status code is {status_code:d}')
def step_response_status_code(context, status_code):
    """Verify the HTTP response status code."""
    assert context.response_status_code == status_code, \
        f"Expected status code {status_code}, got {context.response_status_code}. Response: {context.response_body}"


@then('the response contains an "{field}" token')
def step_response_contains_token(context, field):
    """Verify the response contains a token field."""
    assert field in context.response_json, \
        f"Expected field '{field}' in response, got: {context.response_json}"
    assert context.response_json[field], \
        f"Field '{field}' is empty"
    assert isinstance(context.response_json[field], str), \
        f"Field '{field}' should be a string"
    assert len(context.response_json[field]) > 20, \
        f"Field '{field}' seems too short to be a valid JWT token"


@then('the response does not contain an "{field}" token')
def step_response_does_not_contain_token(context, field):
    """Verify the response does not contain a token field."""
    assert field not in context.response_json or not context.response_json.get(field), \
        f"Field '{field}' should not be present or should be empty, got: {context.response_json}"


@then('the response contains a "refresh" token')
def step_response_contains_refresh_token(context):
    """Verify the response contains a refresh token."""
    return step_response_contains_token(context, "refresh")
