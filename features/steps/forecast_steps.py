"""
Step definitions for Feature 003: Weather Forecast
"""
from behave import when, then
import json


@when('I request the weather forecast for city "{city_name}"')
def step_request_forecast_for_city(context, city_name):
    """Request weather forecast for a city by name."""
    assert hasattr(context, 'city_uuids') and city_name in context.city_uuids, \
        f"City UUID for '{city_name}' not found. Available: {getattr(context, 'city_uuids', {})}"

    city_uuid = context.city_uuids[city_name]

    context.response = context.client.get(
        f'/api/cities/{city_uuid}/forecast',
        HTTP_AUTHORIZATION=f'Bearer {context.access_token}',
    )

    try:
        context.response_data = json.loads(context.response.content)
    except (json.JSONDecodeError, ValueError):
        context.response_data = None


@when('I request the weather forecast for city "{city_name}" for {days:d} days')
def step_request_forecast_for_days(context, city_name, days):
    """Request weather forecast for a specific number of days."""
    assert hasattr(context, 'city_uuids') and city_name in context.city_uuids, \
        f"City UUID for '{city_name}' not found"

    city_uuid = context.city_uuids[city_name]

    context.response = context.client.get(
        f'/api/cities/{city_uuid}/forecast?days={days}',
        HTTP_AUTHORIZATION=f'Bearer {context.access_token}',
    )

    try:
        context.response_data = json.loads(context.response.content)
    except (json.JSONDecodeError, ValueError):
        context.response_data = None


@then('the response contains forecast data')
def step_response_contains_forecast_data(context):
    """Check that the response contains forecast data."""
    assert context.response_data is not None, "Response data is None"
    assert 'forecasts' in context.response_data, \
        f"'forecasts' not found in response: {context.response_data}"
    assert isinstance(context.response_data['forecasts'], list), \
        f"'forecasts' should be a list, got {type(context.response_data['forecasts'])}"


@then('the response contains at most {max_days:d} days of forecast data')
def step_response_contains_max_days(context, max_days):
    """Check that the response contains at most the specified number of days."""
    assert context.response_data is not None, "Response data is None"
    assert 'forecasts' in context.response_data, \
        f"'forecasts' not found in response: {context.response_data}"
    forecast_count = len(context.response_data['forecasts'])
    assert forecast_count <= max_days, \
        f"Expected at most {max_days} days of forecast, got {forecast_count}"


@then('the response contains error message about forecast limit')
def step_response_contains_forecast_limit_error(context):
    """Check that the response contains an error about forecast limit."""
    assert context.response_data is not None, "Response data is None"
    response_str = str(context.response_data).lower()
    assert 'maximum' in response_str or '7' in response_str or 'limit' in response_str, \
        f"Expected error about forecast limit, got: {context.response_data}"


@then('the forecast contains temperature data')
def step_forecast_contains_temperature(context):
    """Check that forecast entries contain temperature data."""
    assert context.response_data is not None, "Response data is None"
    assert 'forecasts' in context.response_data, \
        f"'forecasts' not found in response: {context.response_data}"
    forecasts = context.response_data['forecasts']
    assert len(forecasts) > 0, "No forecast entries found"
    for forecast in forecasts:
        assert 'temperature' in forecast, \
            f"'temperature' not found in forecast entry: {forecast}"


@then('the forecast contains humidity data')
def step_forecast_contains_humidity(context):
    """Check that forecast entries contain humidity data."""
    assert context.response_data is not None, "Response data is None"
    forecasts = context.response_data.get('forecasts', [])
    assert len(forecasts) > 0, "No forecast entries found"
    for forecast in forecasts:
        assert 'humidity' in forecast, \
            f"'humidity' not found in forecast entry: {forecast}"


@then('the forecast contains wind speed data')
def step_forecast_contains_wind_speed(context):
    """Check that forecast entries contain wind speed data."""
    assert context.response_data is not None, "Response data is None"
    forecasts = context.response_data.get('forecasts', [])
    assert len(forecasts) > 0, "No forecast entries found"
    for forecast in forecasts:
        assert 'wind_speed' in forecast, \
            f"'wind_speed' not found in forecast entry: {forecast}"


@then('the forecast contains weather condition description')
def step_forecast_contains_condition(context):
    """Check that forecast entries contain weather condition description."""
    assert context.response_data is not None, "Response data is None"
    forecasts = context.response_data.get('forecasts', [])
    assert len(forecasts) > 0, "No forecast entries found"
    for forecast in forecasts:
        assert 'condition' in forecast, \
            f"'condition' not found in forecast entry: {forecast}"
