"""Authentication step definitions."""
from behave import given, then, when
from behave.runner import Context


@given('I have valid admin credentials')
def step_impl(context: Context) -> None:
    """Create admin user."""
    from django.contrib.auth.models import User

    context.username = 'testadmin'
    context.password = 'testpass123'
    User.objects.create_superuser(context.username, 'admin@test.com', context.password)


@when('I request a JWT token')
def step_impl(context: Context) -> None:
    """Request JWT token."""
    from rest_framework.test import APIClient

    client = APIClient()
    response = client.post('/api/jwt/obtain', {
        'username': context.username,
        'password': context.password,
    })
    context.response = response
    context.token_data = response.json() if response.status_code == 200 else {}


@then('I should receive an access token')
def step_impl(context: Context) -> None:
    """Verify access token received."""
    assert context.response.status_code == 200
    assert 'access' in context.token_data
    context.access_token = context.token_data['access']


@then('I should receive a refresh token')
def step_impl(context: Context) -> None:
    """Verify refresh token received."""
    assert 'refresh' in context.token_data


@given('I have a valid JWT access token')
def step_impl(context: Context) -> None:
    """Create user and get access token."""
    from django.contrib.auth.models import User
    from rest_framework.test import APIClient

    context.username = 'testuser'
    context.password = 'testpass123'
    User.objects.create_user(context.username, 'user@test.com', context.password)

    client = APIClient()
    response = client.post('/api/jwt/obtain', {
        'username': context.username,
        'password': context.password,
    })
    context.access_token = response.json()['access']


@when('I access a protected endpoint')
def step_impl(context: Context) -> None:
    """Access protected endpoint."""
    from rest_framework.test import APIClient

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {context.access_token}')
    context.response = client.get('/api/cities')


@then('I should receive a successful response')
def step_impl(context: Context) -> None:
    """Verify successful response."""
    assert context.response.status_code == 200


@given('I do not have a JWT token')
def step_impl(context: Context) -> None:
    """Ensure no token is set."""
    context.access_token = None


@when('I try to create a city')
def step_impl(context: Context) -> None:
    """Try to create a city without authentication."""
    from rest_framework.test import APIClient

    client = APIClient()
    context.response = client.post('/api/cities', {
        'name': 'Test City',
        'country': 'Test Country',
        'region': 'Test Region',
        'timezone': 'UTC',
        'latitude': 0.0,
        'longitude': 0.0,
    })


@then('I should receive an unauthorized response')
def step_impl(context: Context) -> None:
    """Verify unauthorized response."""
    assert context.response.status_code == 401
