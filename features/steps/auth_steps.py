"""Steps for users, JWT authentication, and permission-gated city writes.

Users and assertion lookups go through the Django ORM (the behave test
database); JWT tokens and authenticated requests go over HTTP to
context.base_url — the behave-django live server backed by that same
database (see api_steps.py).
"""
import parse
import requests
from behave import given, register_type, then, when
from django.contrib.auth import get_user_model

from weather.models import City


@parse.with_pattern(r'[^"]*')
def parse_quoted(text):
    return text


# Registered here as well: importing it from a sibling step module would
# re-execute that module and register duplicate steps.
register_type(Q=parse_quoted)


def resolve_url(context, path):
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return f"{context.base_url}{path}"


def auth_headers(context, role):
    token = context.jwt_tokens[role]
    return {"Authorization": f"Bearer {token}"}


def store_user(context, role, username, password, is_admin):
    user_model = get_user_model()
    user, _ = user_model.objects.get_or_create(username=username)
    user.is_staff = is_admin
    user.is_superuser = is_admin
    user.set_password(password)
    user.save()
    if not hasattr(context, "credentials"):
        context.credentials = {}
    context.credentials[role] = {"username": username, "password": password}


@given('an admin user "{username:Q}" with password "{password:Q}" exists')
def step_admin_user_exists(context, username, password):
    store_user(context, "admin", username, password, is_admin=True)


@given('a regular user "{username:Q}" with password "{password:Q}" exists')
def step_regular_user_exists(context, username, password):
    store_user(context, "regular", username, password, is_admin=False)


@given('the {role:w} user has obtained a JWT access token from "{path:Q}"')
def step_obtain_jwt_token(context, role, path):
    response = requests.post(
        resolve_url(context, path), json=context.credentials[role], timeout=10
    )
    assert response.status_code == 200, (
        f"JWT obtain failed with status {response.status_code}: {response.text}"
    )
    if not hasattr(context, "jwt_tokens"):
        context.jwt_tokens = {}
    context.jwt_tokens[role] = response.json()["access"]


@when(
    'the {role:w} user sends a POST request to "{path:Q}" with '
    'name "{name:Q}", country "{country:Q}", region "{region:Q}", '
    'timezone "{tz:Q}", latitude {latitude:g} and longitude {longitude:g}'
)
def step_user_creates_city(
    context, role, path, name, country, region, tz, latitude, longitude
):
    payload = {
        "name": name,
        "country": country,
        "region": region,
        "timezone": tz,
        "latitude": latitude,
        "longitude": longitude,
    }
    context.response = requests.post(
        resolve_url(context, path),
        json=payload,
        headers=auth_headers(context, role),
        timeout=10,
    )


@when('the {role:w} user sends a GET request to "{path:Q}"')
def step_user_get_request(context, role, path):
    context.response = requests.get(
        resolve_url(context, path), headers=auth_headers(context, role), timeout=10
    )


@when('the {role:w} user sends a DELETE request to "{path:Q}" for the city "{name:Q}"')
def step_user_delete_city(context, role, path, name):
    city = City.objects.get(name=name)
    path = path.replace("<city_uuid>", str(city.uuid))
    context.response = requests.delete(
        resolve_url(context, path), headers=auth_headers(context, role), timeout=10
    )


@when('a client sends a GET request to "{path:Q}" without authentication')
def step_unauthenticated_get(context, path):
    context.response = requests.get(resolve_url(context, path), timeout=10)


@when('a client sends a POST request to "{path:Q}" with name "{name:Q}" and no authentication')
def step_unauthenticated_city_post(context, path, name):
    context.response = requests.post(
        resolve_url(context, path), json={"name": name}, timeout=10
    )


@then('a city named "{name:Q}" exists in the database')
def step_city_in_database(context, name):
    assert City.objects.filter(name=name).exists(), (
        f'no city named "{name}" exists in the database'
    )


@then('no city named "{name:Q}" exists in the database')
def step_city_not_in_database(context, name):
    assert not City.objects.filter(name=name).exists(), (
        f'a city named "{name}" unexpectedly exists in the database'
    )
