from behave import given, when, then
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@given("I am an unauthenticated user")
def step_unauthenticated(context):
    context.client = APIClient()


@given("I am authenticated as admin")
def step_admin(context):
    context.client = APIClient()
    user, _ = User.objects.get_or_create(
        username="test_admin",
        defaults={"is_staff": True, "is_superuser": True},
    )
    user.set_password("password")
    user.save()
    response = context.client.post(
        "/api/jwt/obtain",
        {"username": "test_admin", "password": "password"},
        format="json",
    )
    token = response.data["access"]
    context.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


@given("I am authenticated as a regular user")
def step_regular_user(context):
    context.client = APIClient()
    user, _ = User.objects.get_or_create(
        username="test_user",
        defaults={"is_staff": False},
    )
    user.set_password("password")
    user.save()
    response = context.client.post(
        "/api/jwt/obtain",
        {"username": "test_user", "password": "password"},
        format="json",
    )
    token = response.data["access"]
    context.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


@when("I GET /api/cities")
def step_get_cities(context):
    context.response = context.client.get("/api/cities/")


@when("I POST /api/cities with Tokyo data")
def step_post_tokyo(context):
    context.response = context.client.post(
        "/api/cities/",
        {
            "name": "Tokyo",
            "country": "Japan",
            "region": "Asia",
            "timezone": "Asia/Tokyo",
            "latitude": 35.6762,
            "longitude": 139.6503,
        },
        format="json",
    )


@when("I POST /api/cities with Delhi data")
def step_post_delhi(context):
    context.response = context.client.post(
        "/api/cities/",
        {
            "name": "Delhi",
            "country": "India",
            "region": "Asia",
            "timezone": "Asia/Kolkata",
            "latitude": 28.6139,
            "longitude": 77.2090,
        },
        format="json",
    )


@then("the response status is {status_code:d}")
def step_status_code(context, status_code):
    assert context.response.status_code == status_code, (
        f"Expected {status_code}, got {context.response.status_code}: {context.response.data}"
    )


@then("the response contains a results list")
def step_results_list(context):
    assert "results" in context.response.data, f"No 'results' key in {context.response.data}"


@then("the response contains the city name {name}")
def step_city_name(context, name):
    assert context.response.data.get("name") == name, (
        f"Expected name={name}, got {context.response.data}"
    )


@when("I query GraphQL for all cities")
def step_graphql_cities(context):
    import json
    context.response = context.client.post(
        "/graphql/",
        data=json.dumps({"query": "{ cities { uuid name country } }"}),
        content_type="application/json",
    )


@then("the GraphQL response contains a cities list")
def step_graphql_cities_list(context):
    import json
    data = json.loads(context.response.content)
    assert "data" in data, f"No 'data' key in {data}"
    assert "cities" in data["data"], f"No 'cities' key in {data['data']}"
    assert isinstance(data["data"]["cities"], list)
