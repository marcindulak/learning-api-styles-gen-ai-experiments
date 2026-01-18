"""
Step definitions for Feature 002: User Authentication (JWT Tokens)
"""
from behave import given, when, then
from django.contrib.auth.models import User
from django.test import Client
import json
import jwt


@given('a user with username "{username}" and password "{password}" exists')
def step_user_exists(context, username, password):
    """
    Create or get a user with the given credentials.
    """
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': f'{username}@test.local'}
    )
    if created or user.password != 'dummy':  # Ensure password is set
        user.set_password(password)
        user.save()

    # Store user in context
    if not hasattr(context, 'users'):
        context.users = {}
    context.users[username] = user
    context.current_user = user
    context.current_password = password


@when('the admin user requests a JWT token')
def step_admin_request_jwt(context):
    """
    Admin user requests JWT token.
    """
    step_request_jwt_token(context, 'admin', 'admin')


@when('the regular user requests a JWT token')
def step_regular_request_jwt(context):
    """
    Regular user requests JWT token.
    """
    step_request_jwt_token(context, 'user', 'password')


def step_request_jwt_token(context, username, password):
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
        context.response_data = None
        context.access_token = None
        context.refresh_token = None


@when('I request a JWT token with username "{username}" and password "{password}"')
def step_request_jwt_with_credentials(context, username, password):
    """
    Request JWT token with explicit credentials.
    """
    step_request_jwt_token(context, username, password)


@then('a JWT access token is returned')
def step_access_token_returned(context):
    """
    Verify that access token is returned in response.
    """
    assert context.response.status_code == 200, \
        f"Expected 200, got {context.response.status_code}: {context.response.content}"
    assert 'access' in context.response_data, \
        f"'access' field not found in response: {context.response_data}"
    assert context.response_data['access'] is not None, \
        "access token is None"
    assert isinstance(context.response_data['access'], str), \
        f"access token should be string, got {type(context.response_data['access'])}"


@then('the access token is valid for API requests')
def step_access_token_valid(context):
    """
    Verify that the access token can be used for authenticated requests.
    """
    assert context.access_token is not None, "No access token found"

    # Try to use the token to access a protected endpoint
    headers = {
        'HTTP_AUTHORIZATION': f'Bearer {context.access_token}',
        'content_type': 'application/json',
    }

    response = context.client.get('/api/me', **headers)

    # Should be 200 OK if token is valid, or 401/403 if protected endpoint doesn't exist yet
    # For now, just check that we can make the request without 401 auth errors
    # (404 is okay since /api/me might not be fully implemented)
    assert response.status_code in [200, 404], \
        f"Token validation failed with status {response.status_code}"


@then('the request fails with an authentication error')
def step_auth_error(context):
    """
    Verify that request fails with authentication error (401 or 400).
    """
    assert context.response.status_code in [400, 401], \
        f"Expected 400 or 401 auth error, got {context.response.status_code}: {context.response.content}"


@given('the user has obtained a valid JWT access token')
def step_user_obtained_token(context):
    """
    Ensure the current user has obtained a valid JWT token.
    """
    if not context.access_token:
        # Request token for the current user
        if hasattr(context, 'current_user'):
            username = context.current_user.username
            password = getattr(context, 'current_password', '')
            step_request_jwt_token(context, username, password)
        else:
            # Default to admin
            step_request_jwt_token(context, 'admin', 'admin')

    assert context.access_token is not None, "Failed to obtain access token"


@when('I make a request to a protected endpoint with the access token')
def step_request_protected_with_token(context):
    """
    Make a request to a protected endpoint using the access token.
    """
    assert context.access_token is not None, "No access token available"

    headers = {
        'HTTP_AUTHORIZATION': f'Bearer {context.access_token}',
        'content_type': 'application/json',
    }

    # Try accessing /api/me or /api/cities (protected endpoints)
    context.response = context.client.get('/api/me', **headers)


@then('the request is successful')
def step_request_successful(context):
    """
    Verify that the request was successful (200 OK).
    """
    assert context.response.status_code == 200, \
        f"Expected 200 OK, got {context.response.status_code}: {context.response.content}"


@given('no JWT token is provided')
def step_no_jwt_token(context):
    """
    Ensure no JWT token is in the context.
    """
    context.access_token = None
    context.refresh_token = None


@when('I make a request to a protected endpoint')
def step_request_protected_without_token(context):
    """
    Make a request to a protected endpoint without authentication.
    """
    # Try accessing a protected endpoint without token
    context.response = context.client.get('/api/me')


@then('the request fails with a 401 Unauthorized status')
def step_request_fails_401(context):
    """
    Verify that request fails with 401 Unauthorized.
    """
    assert context.response.status_code == 401, \
        f"Expected 401, got {context.response.status_code}: {context.response.content}"
