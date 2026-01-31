"""
Step definitions for Feature 004: Weather Historical Data
"""
from behave import given, when, then
from datetime import datetime
import json


@given('historical weather data exists for city "{city_name}" on date "{date_str}"')
def step_historical_data_exists(context, city_name, date_str):
    """Create historical weather data for a city on a specific date."""
    assert hasattr(context, 'city_uuids') and city_name in context.city_uuids, \
        f"City UUID for '{city_name}' not found"

    city_uuid = context.city_uuids[city_name]

    # Create historical data via API
    historical_data = {
        'city_uuid': str(city_uuid),
        'date': date_str,
        'temperature': 22.5,
        'humidity': 65.0,
        'wind_speed': 8.5,
        'condition': 'Partly cloudy',
    }

    context.response = context.client.post(
        f'/api/cities/{city_uuid}/historical',
        data=json.dumps(historical_data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {context.access_token}',
    )

    # Store the data for verification
    if not hasattr(context, 'historical_data'):
        context.historical_data = {}
    context.historical_data[(city_name, date_str)] = historical_data


@when('I request historical weather data for city "{city_name}" on date "{date_str}"')
def step_request_historical_data(context, city_name, date_str):
    """Request historical weather data for a city on a specific date."""
    assert hasattr(context, 'city_uuids') and city_name in context.city_uuids, \
        f"City UUID for '{city_name}' not found"

    city_uuid = context.city_uuids[city_name]

    context.response = context.client.get(
        f'/api/cities/{city_uuid}/historical?date={date_str}',
        HTTP_AUTHORIZATION=f'Bearer {context.access_token}',
    )

    try:
        context.response_data = json.loads(context.response.content)
    except (json.JSONDecodeError, ValueError):
        context.response_data = None


@then('the response contains weather data for date "{date_str}"')
def step_response_contains_date(context, date_str):
    """Check that the response contains weather data for the specified date."""
    assert context.response_data is not None, "Response data is None"
    assert 'date' in context.response_data, \
        f"'date' not found in response: {context.response_data}"
    assert context.response_data['date'] == date_str, \
        f"Expected date '{date_str}', got '{context.response_data.get('date')}'"


@then('the historical data contains temperature')
def step_historical_contains_temperature(context):
    """Check that the historical data contains temperature."""
    assert context.response_data is not None, "Response data is None"
    assert 'temperature' in context.response_data, \
        f"'temperature' not found in response: {context.response_data}"


@then('the historical data contains humidity')
def step_historical_contains_humidity(context):
    """Check that the historical data contains humidity."""
    assert context.response_data is not None, "Response data is None"
    assert 'humidity' in context.response_data, \
        f"'humidity' not found in response: {context.response_data}"


@then('the historical data contains wind speed')
def step_historical_contains_wind_speed(context):
    """Check that the historical data contains wind speed."""
    assert context.response_data is not None, "Response data is None"
    assert 'wind_speed' in context.response_data, \
        f"'wind_speed' not found in response: {context.response_data}"


@then('the historical data contains weather condition')
def step_historical_contains_condition(context):
    """Check that the historical data contains weather condition."""
    assert context.response_data is not None, "Response data is None"
    assert 'condition' in context.response_data, \
        f"'condition' not found in response: {context.response_data}"
