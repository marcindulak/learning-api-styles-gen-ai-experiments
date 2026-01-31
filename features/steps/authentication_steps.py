"""
Step definitions for Feature 001: JWT Authentication
"""
from behave import given, when, then
from django.contrib.auth.models import User
from django.test import Client
import json


@given('the Weather Forecast Service is running')
def step_service_running(context):
    """
    Verify the service is running by checking the test client is available.
    """
    if not hasattr(context, 'client'):
        context.client = Client()
    # The service is running if we have a test client
    assert context.client is not None


@given('an admin user exists with username "{username}" and password "{password}"')
def step_admin_user_exists(context, username, password):
    """
    Create or get an admin user with the given credentials.
    """
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': f'{username}@test.local', 'is_staff': True, 'is_superuser': True}
    )
    if created or not user.check_password(password):
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()

    if not hasattr(context, 'users'):
        context.users = {}
    context.users[username] = user
    context.admin_user = user
    context.admin_password = password


@given('a regular user "{username}" exists with password "{password}"')
def step_regular_user_exists(context, username, password):
    """
    Create or get a regular user with the given credentials.
    """
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': f'{username}@test.local', 'is_staff': False, 'is_superuser': False}
    )
    if created or not user.check_password(password):
        user.set_password(password)
        user.is_staff = False
        user.is_superuser = False
        user.save()

    if not hasattr(context, 'users'):
        context.users = {}
    context.users[username] = user

    # Store the password for later use when obtaining JWT token
    if not hasattr(context, 'user_passwords'):
        context.user_passwords = {}
    context.user_passwords[username] = password


def request_jwt_token(context, username, password):
    """
    Helper: Request JWT token for a user.
    """
    if not hasattr(context, 'client'):
        context.client = Client()

    payload = {
        'username': username,
        'password': password,
    }

    context.response = context.client.post(
        '/api/jwt/obtain',
        data=json.dumps(payload),
        content_type='application/json',
    )

    if context.response.status_code == 200:
        context.response_data = json.loads(context.response.content)
        context.access_token = context.response_data.get('access')
        context.refresh_token = context.response_data.get('refresh')
    else:
        try:
            context.response_data = json.loads(context.response.content)
        except (json.JSONDecodeError, ValueError):
            context.response_data = None
        context.access_token = None
        context.refresh_token = None


@when('I request a JWT token with username "{username}" and password "{password}"')
def step_request_jwt_with_credentials(context, username, password):
    """
    Request JWT token with explicit credentials.
    """
    request_jwt_token(context, username, password)


@given('I have obtained a JWT access token for user "{username}"')
def step_have_access_token(context, username):
    """
    Obtain a JWT access token for the specified user.
    """
    # Get the password for this user from context or use defaults
    if username == 'admin':
        password = getattr(context, 'admin_password', 'admin')
    elif hasattr(context, 'user_passwords') and username in context.user_passwords:
        password = context.user_passwords[username]
    else:
        password = 'password'  # Default password for test users

    request_jwt_token(context, username, password)
    assert context.access_token is not None, f"Failed to obtain access token for {username}"


@when('I make an authenticated GET request to "{endpoint}"')
def step_authenticated_get_request(context, endpoint):
    """
    Make an authenticated GET request to an endpoint.
    """
    assert context.access_token is not None, "No access token available"

    context.response = context.client.get(
        endpoint,
        HTTP_AUTHORIZATION=f'Bearer {context.access_token}',
        content_type='application/json',
    )

    try:
        context.response_data = json.loads(context.response.content)
    except (json.JSONDecodeError, ValueError):
        context.response_data = None


@when('I make an unauthenticated POST request to "{endpoint}"')
def step_unauthenticated_post_request(context, endpoint):
    """
    Make an unauthenticated POST request to an endpoint.
    """
    context.response = context.client.post(
        endpoint,
        data=json.dumps({}),
        content_type='application/json',
    )

    try:
        context.response_data = json.loads(context.response.content)
    except (json.JSONDecodeError, ValueError):
        context.response_data = None


@then('I receive a response with status code {status_code:d}')
def step_check_status_code(context, status_code):
    """
    Check the response status code.
    """
    assert context.response.status_code == status_code, \
        f"Expected status code {status_code}, got {context.response.status_code}. Response: {context.response.content}"


@then('the response contains an "{field}" token')
@then('the response contains a "{field}" token')
def step_response_contains_token(context, field):
    """
    Check that the response contains a token field.
    """
    assert context.response_data is not None, "Response data is None"
    assert field in context.response_data, \
        f"'{field}' field not found in response: {context.response_data}"
    assert context.response_data[field] is not None, \
        f"'{field}' token is None"
    assert isinstance(context.response_data[field], str), \
        f"'{field}' token should be string, got {type(context.response_data[field])}"
    assert len(context.response_data[field]) > 0, \
        f"'{field}' token should not be empty"
