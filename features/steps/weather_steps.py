"""
Step definitions for Feature 006: REST API Weather Indicators
"""
from behave import given, when, then
from django.utils import timezone
import json


@given('current weather data exists for city "{city_name}"')
def step_current_weather_exists(context, city_name):
    """Create current weather data for a city."""
    assert hasattr(context, 'city_uuids') and city_name in context.city_uuids, \
        f"City UUID for '{city_name}' not found"

    city_uuid = context.city_uuids[city_name]

    # Create current weather data via API
    weather_data = {
        'temperature': 22.5,
        'humidity': 65.0,
        'wind_speed': 8.5,
        'pressure': 1013.25,
        'condition_code': 'partly_cloudy',
        'condition': 'Partly cloudy',
        'timestamp': timezone.now().isoformat(),
    }

    response = context.client.post(
        f'/api/cities/{city_uuid}/weather',
        data=json.dumps(weather_data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {context.access_token}',
    )

    # Store for verification
    if not hasattr(context, 'weather_data'):
        context.weather_data = {}
    context.weather_data[city_name] = weather_data


@when('I request current weather for city "{city_name}"')
def step_request_current_weather(context, city_name):
    """Request current weather for a city by name."""
    assert hasattr(context, 'city_uuids') and city_name in context.city_uuids, \
        f"City UUID for '{city_name}' not found"

    city_uuid = context.city_uuids[city_name]

    context.response = context.client.get(
        f'/api/cities/{city_uuid}/weather',
        HTTP_AUTHORIZATION=f'Bearer {context.access_token}',
    )

    try:
        context.response_data = json.loads(context.response.content)
    except (json.JSONDecodeError, ValueError):
        context.response_data = None


@when('I request current weather for non-existent city UUID "{uuid}"')
def step_request_weather_nonexistent_city(context, uuid):
    """Request current weather for a non-existent city UUID."""
    context.response = context.client.get(
        f'/api/cities/{uuid}/weather',
        HTTP_AUTHORIZATION=f'Bearer {context.access_token}',
    )

    try:
        context.response_data = json.loads(context.response.content)
    except (json.JSONDecodeError, ValueError):
        context.response_data = None


@then('the response contains temperature in Celsius')
def step_response_contains_temperature(context):
    """Check that the response contains temperature."""
    assert context.response_data is not None, "Response data is None"
    assert 'temperature' in context.response_data, \
        f"'temperature' not found in response: {context.response_data}"
    assert isinstance(context.response_data['temperature'], (int, float)), \
        f"'temperature' should be a number, got {type(context.response_data['temperature'])}"


@then('the response contains humidity percentage')
def step_response_contains_humidity(context):
    """Check that the response contains humidity."""
    assert context.response_data is not None, "Response data is None"
    assert 'humidity' in context.response_data, \
        f"'humidity' not found in response: {context.response_data}"
    assert isinstance(context.response_data['humidity'], (int, float)), \
        f"'humidity' should be a number, got {type(context.response_data['humidity'])}"


@then('the response contains wind speed in meters per second')
def step_response_contains_wind_speed(context):
    """Check that the response contains wind speed."""
    assert context.response_data is not None, "Response data is None"
    assert 'wind_speed' in context.response_data, \
        f"'wind_speed' not found in response: {context.response_data}"
    assert isinstance(context.response_data['wind_speed'], (int, float)), \
        f"'wind_speed' should be a number, got {type(context.response_data['wind_speed'])}"


@then('the response contains atmospheric pressure')
def step_response_contains_pressure(context):
    """Check that the response contains atmospheric pressure."""
    assert context.response_data is not None, "Response data is None"
    assert 'pressure' in context.response_data, \
        f"'pressure' not found in response: {context.response_data}"
    assert isinstance(context.response_data['pressure'], (int, float)), \
        f"'pressure' should be a number, got {type(context.response_data['pressure'])}"


@then('the response contains weather condition code')
def step_response_contains_condition_code(context):
    """Check that the response contains weather condition code."""
    assert context.response_data is not None, "Response data is None"
    assert 'condition_code' in context.response_data, \
        f"'condition_code' not found in response: {context.response_data}"
    assert isinstance(context.response_data['condition_code'], str), \
        f"'condition_code' should be a string, got {type(context.response_data['condition_code'])}"


@then('the response contains weather condition description')
def step_response_contains_condition_description(context):
    """Check that the response contains weather condition description."""
    assert context.response_data is not None, "Response data is None"
    assert 'condition' in context.response_data, \
        f"'condition' not found in response: {context.response_data}"
    assert isinstance(context.response_data['condition'], str), \
        f"'condition' should be a string, got {type(context.response_data['condition'])}"


@then('the response contains a timestamp field')
def step_response_contains_timestamp(context):
    """Check that the response contains a timestamp field."""
    assert context.response_data is not None, "Response data is None"
    assert 'timestamp' in context.response_data, \
        f"'timestamp' not found in response: {context.response_data}"


@then('the response contains the city UUID')
def step_response_contains_city_uuid(context):
    """Check that the response contains the city UUID."""
    assert context.response_data is not None, "Response data is None"
    assert 'city_uuid' in context.response_data, \
        f"'city_uuid' not found in response: {context.response_data}"
