"""
Step definitions for user management.
"""
import json
import subprocess

from behave import given, then, when


@given('a user exists with username "{username}" and password "{password}"')
def step_create_user(context, username, password):
    """Create a regular user."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    User.objects.create_user(username=username, password=password)


@when('I request a JWT access token with username "{username}" and password "{password}"')
def step_request_jwt_token(context, username, password):
    """Request JWT access token."""
    credentials = json.dumps({'username': username, 'password': password})

    result = subprocess.run(
        [
            'curl',
            '--data', credentials,
            '--header', 'Content-Type: application/json',
            '--request', 'POST',
            '--silent',
            'http://localhost:8000/api/jwt/obtain',
        ],
        capture_output=True,
        text=True,
    )

    context.response_status = result.returncode
    context.response_body = result.stdout

    # Parse response code from headers (curl doesn't show by default)
    # Use another curl to get status code
    result_with_code = subprocess.run(
        [
            'curl',
            '--data', credentials,
            '--header', 'Content-Type: application/json',
            '--request', 'POST',
            '--silent',
            '--output', '/dev/null',
            '--write-out', '%{http_code}',
            'http://localhost:8000/api/jwt/obtain',
        ],
        capture_output=True,
        text=True,
    )

    context.response_status_code = int(result_with_code.stdout)


@then('the response status code is {status_code:d}')
def step_check_status_code(context, status_code):
    """Check response status code."""
    assert context.response_status_code == status_code, \
        f'Expected {status_code}, got {context.response_status_code}'


@then('the response contains a field "{field_name}"')
def step_check_field_exists(context, field_name):
    """Check that response contains a field."""
    response_data = json.loads(context.response_body)
    assert field_name in response_data, \
        f'Field {field_name} not found in response: {response_data}'
