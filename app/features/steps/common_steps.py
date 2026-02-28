"""Common step definitions for BDD tests."""

import hashlib
import hmac
import json
from datetime import date, timedelta
from decimal import Decimal

from behave import given, then, when
from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client

from weather.models import City, WeatherRecord


@given("the database is seeded with cities")
def step_seed_cities(context):
    from weather.management.commands.seed_cities import CITIES

    for city_data in CITIES:
        City.objects.get_or_create(name=city_data["name"], defaults=city_data)
    context.client = Client()


@given("I am authenticated as admin")
def step_auth_admin(context):
    context.client = Client()
    user, _ = User.objects.get_or_create(
        username="admin",
        defaults={"is_staff": True, "is_superuser": True},
    )
    user.set_password("admin")
    user.save()
    response = context.client.post(
        "/api/jwt/obtain",
        data=json.dumps({"username": "admin", "password": "admin"}),
        content_type="application/json",
    )
    context.access_token = response.json()["access"]


@given("a test city exists")
def step_create_test_city(context):
    context.test_city, _ = City.objects.get_or_create(
        name="TestCity",
        defaults={
            "country": "Testland",
            "region": "Test Region",
            "timezone": "UTC",
            "latitude": Decimal("0.000000"),
            "longitude": Decimal("0.000000"),
        },
    )


@given("a test city exists with weather records")
def step_city_with_records(context):
    context.client = Client()
    context.test_city, _ = City.objects.get_or_create(
        name="TestCityWeather",
        defaults={
            "country": "Testland",
            "region": "Test Region",
            "timezone": "UTC",
            "latitude": Decimal("10.000000"),
            "longitude": Decimal("20.000000"),
        },
    )
    from django.utils import timezone

    WeatherRecord.objects.get_or_create(
        city=context.test_city,
        timestamp=timezone.now(),
        defaults={
            "temperature": Decimal("25.0"),
            "feels_like": Decimal("26.0"),
            "humidity": 60,
            "pressure": Decimal("1013.0"),
            "wind_speed": Decimal("5.0"),
            "wind_direction": 180,
            "precipitation": Decimal("0.0"),
            "visibility": 10000,
            "uv_index": Decimal("5.0"),
            "cloud_cover": 30,
            "description": "Partly cloudy",
        },
    )


@given("I have a valid refresh token")
def step_get_refresh_token(context):
    context.client = Client()
    user, _ = User.objects.get_or_create(
        username="admin",
        defaults={"is_staff": True, "is_superuser": True},
    )
    user.set_password("admin")
    user.save()
    response = context.client.post(
        "/api/jwt/obtain",
        data=json.dumps({"username": "admin", "password": "admin"}),
        content_type="application/json",
    )
    context.refresh_token = response.json()["refresh"]


def _auth_headers(context):
    headers = {}
    if hasattr(context, "access_token"):
        headers["HTTP_AUTHORIZATION"] = f"Bearer {context.access_token}"
    return headers


@when('I GET "{url}"')
def step_get_url(context, url):
    context.response = context.client.get(url, **_auth_headers(context))


@when("I GET a city by its UUID")
def step_get_city_by_uuid(context):
    city = City.objects.first()
    context.response = context.client.get(f"/api/cities/{city.uuid}")


@when('I POST "{url}" with a valid city payload')
def step_post_city(context, url):
    payload = {
        "name": "Copenhagen",
        "country": "Denmark",
        "region": "Europe",
        "timezone": "Europe/Copenhagen",
        "latitude": 55.676100,
        "longitude": 12.568300,
    }
    context.response = context.client.post(
        url,
        data=json.dumps(payload),
        content_type="application/json",
        **_auth_headers(context),
    )


@when('I POST "{url}" with valid credentials')
def step_post_valid_creds(context, url):
    context.client = Client()
    user, _ = User.objects.get_or_create(
        username="admin",
        defaults={"is_staff": True, "is_superuser": True},
    )
    user.set_password("admin")
    user.save()
    context.response = context.client.post(
        url,
        data=json.dumps({"username": "admin", "password": "admin"}),
        content_type="application/json",
    )


@when('I POST "{url}" with invalid credentials')
def step_post_invalid_creds(context, url):
    context.client = Client()
    context.response = context.client.post(
        url,
        data=json.dumps({"username": "wrong", "password": "wrong"}),
        content_type="application/json",
    )


@when('I POST "{url}" with the refresh token')
def step_post_refresh(context, url):
    context.response = context.client.post(
        url,
        data=json.dumps({"refresh": context.refresh_token}),
        content_type="application/json",
    )


@when("I DELETE the test city")
def step_delete_city(context):
    context.response = context.client.delete(
        f"/api/cities/{context.test_city.uuid}",
        **_auth_headers(context),
    )


@when("I POST a weather record for the test city")
def step_post_weather_record(context):
    from django.utils import timezone

    payload = {
        "timestamp": timezone.now().isoformat(),
        "temperature": 25.0,
        "feels_like": 26.0,
        "humidity": 60,
        "pressure": 1013.0,
        "wind_speed": 5.0,
        "wind_direction": 180,
        "precipitation": 0.0,
        "visibility": 10000,
        "uv_index": 5.0,
        "cloud_cover": 30,
        "description": "Partly cloudy",
    }
    context.response = context.client.post(
        f"/api/cities/{context.test_city.uuid}/weather",
        data=json.dumps(payload),
        content_type="application/json",
        **_auth_headers(context),
    )


@when("I GET weather records for the test city")
def step_get_weather_records(context):
    context.response = context.client.get(
        f"/api/cities/{context.test_city.uuid}/weather"
    )


@when("I POST a forecast for the test city")
def step_post_forecast(context):
    payload = {
        "forecast_date": str(date.today()),
        "temperature_high": 30.0,
        "temperature_low": 20.0,
        "humidity": 50,
        "precipitation_prob": 20,
        "wind_speed": 10.0,
        "description": "Sunny",
    }
    context.response = context.client.post(
        f"/api/cities/{context.test_city.uuid}/forecast",
        data=json.dumps(payload),
        content_type="application/json",
        **_auth_headers(context),
    )


@when("I POST a forecast with a date more than 7 days out")
def step_post_forecast_too_far(context):
    payload = {
        "forecast_date": str(date.today() + timedelta(days=10)),
        "temperature_high": 30.0,
        "temperature_low": 20.0,
        "humidity": 50,
        "precipitation_prob": 20,
        "wind_speed": 10.0,
        "description": "Sunny",
    }
    context.response = context.client.post(
        f"/api/cities/{context.test_city.uuid}/forecast",
        data=json.dumps(payload),
        content_type="application/json",
        **_auth_headers(context),
    )


@when("I POST a forecast with high temp less than low temp")
def step_post_forecast_invalid_temps(context):
    payload = {
        "forecast_date": str(date.today()),
        "temperature_high": 10.0,
        "temperature_low": 20.0,
        "humidity": 50,
        "precipitation_prob": 20,
        "wind_speed": 10.0,
        "description": "Sunny",
    }
    context.response = context.client.post(
        f"/api/cities/{context.test_city.uuid}/forecast",
        data=json.dumps(payload),
        content_type="application/json",
        **_auth_headers(context),
    )


@when("I POST a webhook ping event with valid signature")
def step_post_webhook_valid(context):
    context.client = Client()
    payload = json.dumps({"zen": "test"}).encode()
    secret = settings.WEBHOOK_SECRET.encode("utf-8")
    sig = "sha256=" + hmac.new(secret, payload, hashlib.sha256).hexdigest()
    context.response = context.client.post(
        "/api/webhooks/github",
        data=payload,
        content_type="application/json",
        HTTP_X_HUB_SIGNATURE_256=sig,
        HTTP_X_GITHUB_EVENT="ping",
    )


@when("I POST a webhook event with invalid signature")
def step_post_webhook_invalid(context):
    context.client = Client()
    context.response = context.client.post(
        "/api/webhooks/github",
        data=json.dumps({"zen": "test"}),
        content_type="application/json",
        HTTP_X_HUB_SIGNATURE_256="sha256=invalidsignature",
        HTTP_X_GITHUB_EVENT="ping",
    )


@then("the response status is {status_code:d}")
def step_check_status(context, status_code):
    assert context.response.status_code == status_code, (
        f"Expected {status_code}, got {context.response.status_code}: "
        f"{context.response.content.decode()}"
    )


@then("the response contains a paginated list")
def step_check_paginated(context):
    data = context.response.json()
    assert "results" in data
    assert "count" in data


@then('the results contain "{name}"')
def step_results_contain(context, name):
    data = context.response.json()
    names = [r["name"] for r in data["results"]]
    assert name in names, f"{name} not found in {names}"


@then("the response contains the created city")
def step_check_created_city(context):
    data = context.response.json()
    assert "uuid" in data
    assert "name" in data


@then("the response contains the city details")
def step_check_city_details(context):
    data = context.response.json()
    assert "uuid" in data
    assert "name" in data
    assert "country" in data


@then('the response contains "access" and "refresh" tokens')
def step_check_jwt_tokens(context):
    data = context.response.json()
    assert "access" in data
    assert "refresh" in data


@then('the response contains a new "access" token')
def step_check_new_access(context):
    data = context.response.json()
    assert "access" in data


@then("the response contains weather records")
def step_check_weather_records(context):
    data = context.response.json()
    assert "results" in data


@then('the response contains "{text}"')
def step_response_contains_text(context, text):
    data = context.response.json()
    assert text in json.dumps(data), f'"{text}" not found in {data}'
