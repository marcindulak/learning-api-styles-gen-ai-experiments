import json
import uuid

from behave import given, then, when
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from weather_service.models import City


@given('an admin user is authenticated with JWT token')
def step_admin_authenticated_with_jwt(context):
    """
    Create an admin user and obtain JWT token for authentication.
    """
    user = User.objects.create_user(
        username="admin",
        password="admin",
        is_staff=True,
        is_superuser=True,
    )
    refresh = RefreshToken.for_user(user)
    context.access_token = str(refresh.access_token)
    context.user = user


@when('requesting JWT token with username "{username}" and password "{password}"')
def step_request_jwt_token(context, username, password):
    """
    Request JWT token with given credentials.
    """
    client = APIClient()
    response = client.post(
        "/api/jwt/obtain",
        {"username": username, "password": password},
        format="json",
    )
    context.response = response
    if response.status_code == 200:
        context.access_token = response.data.get("access")


@then('a valid JWT access token is returned')
def step_valid_jwt_token_returned(context):
    """
    Verify that a valid JWT access token is returned.
    """
    assert context.response.status_code == 200
    assert "access" in context.response.data
    assert context.response.data["access"] is not None
    assert len(context.response.data["access"]) > 0


@when('creating a city via POST to "{endpoint}" with data')
def step_create_city_via_post(context, endpoint):
    """
    Create a city via POST request to the REST API.
    """
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {context.access_token}")
    
    row = context.table[0]
    payload = {
        "name": row["name"],
        "country": row["country"],
        "region": row["region"],
        "timezone": row["timezone"],
        "latitude": row["latitude"],
        "longitude": row["longitude"],
    }
    
    response = client.post(endpoint, payload, format="json")
    context.response = response


@then('the response status is {status_code:d}')
def step_response_status_is(context, status_code):
    """
    Verify the response status code.
    """
    assert context.response.status_code == status_code, \
        f"Expected status {status_code}, got {context.response.status_code}. Response: {context.response.data}"


@then('the response contains city UUID')
def step_response_contains_city_uuid(context):
    """
    Verify the response contains a city UUID.
    """
    assert "uuid" in context.response.data
    try:
        uuid.UUID(str(context.response.data["uuid"]))
    except ValueError:
        raise AssertionError(f"Invalid UUID: {context.response.data['uuid']}")


@then('the response contains city name "{name}"')
def step_response_contains_city_name(context, name):
    """
    Verify the response contains the specified city name.
    """
    assert context.response.data["name"] == name


@when('retrieving city via GET from "{endpoint}"')
def step_retrieve_city_via_get(context, endpoint):
    """
    Retrieve a city via GET request.
    """
    client = APIClient()
    response = client.get(endpoint)
    context.response = response


@when('searching cities via GET from "{endpoint}"')
def step_search_cities_via_get(context, endpoint):
    """
    Search cities via GET request with query parameters.
    """
    client = APIClient()
    response = client.get(endpoint)
    context.response = response


@then('the results contain city "{name}"')
def step_results_contain_city(context, name):
    """
    Verify the search results contain the specified city.
    """
    assert "results" in context.response.data
    city_names = [city["name"] for city in context.response.data["results"]]
    assert name in city_names, f"City {name} not found in results: {city_names}"


@when('updating city via PATCH to "{endpoint}" with data')
def step_update_city_via_patch(context, endpoint):
    """
    Update a city via PATCH request.
    """
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {context.access_token}")
    
    row = context.table[0]
    payload = {
        "latitude": row["latitude"],
        "longitude": row["longitude"],
    }
    
    response = client.patch(endpoint, payload, format="json")
    context.response = response


@then('the response contains updated latitude {latitude:f}')
def step_response_contains_updated_latitude(context, latitude):
    """
    Verify the response contains the updated latitude.
    """
    response_latitude = float(context.response.data["latitude"])
    assert abs(response_latitude - latitude) < 0.0001, \
        f"Expected latitude {latitude}, got {response_latitude}"


@when('deleting city via DELETE from "{endpoint}"')
def step_delete_city_via_delete(context, endpoint):
    """
    Delete a city via DELETE request.
    """
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {context.access_token}")
    
    response = client.delete(endpoint)
    context.response = response


@then('the city "{name}" no longer exists in the system')
def step_city_no_longer_exists(context, name):
    """
    Verify the city no longer exists in the database.
    """
    assert not City.objects.filter(name=name).exists()
