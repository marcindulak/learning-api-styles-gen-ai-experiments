"""Step definitions for weather data storage features."""

import json
import subprocess
from datetime import datetime, timedelta

from behave import given, then, when

from src.weather.models import City, CurrentWeather


@given('weather data exists for "{city_name}" on "{timestamp}"')
def step_weather_data_exists(context, city_name: str, timestamp: str):
    """Create weather data for a city at a specific timestamp."""
    city = City.objects.get(name=city_name)
    timestamp_dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

    if not CurrentWeather.objects.filter(city=city, timestamp=timestamp_dt).exists():
        CurrentWeather.objects.create(
            city=city,
            temperature=15.5,
            humidity=65,
            pressure=1013,
            wind_speed=12.3,
            conditions='Partly Cloudy',
            timestamp=timestamp_dt
        )


@given('today is "{date}"')
def step_set_today(context, date: str):
    """Store the current date for validation."""
    context.today = datetime.strptime(date, '%Y-%m-%d').date()


@when('I send a POST request to "{endpoint}" with data:')
def step_post_weather_data(context, endpoint: str):
    """Send a POST request with weather data from the table."""
    data = {}
    headers = context.table.headings
    if len(headers) == 2:
        data[headers[0].strip()] = headers[1].strip()

    for row in context.table:
        field_name = row.cells[0].strip()
        field_value = row.cells[1].strip()
        data[field_name] = field_value

    # Convert numeric fields
    for field in ['temperature', 'wind_speed', 'latitude', 'longitude']:
        if field in data:
            data[field] = float(data[field])

    for field in ['humidity', 'pressure']:
        if field in data:
            data[field] = int(data[field])

    payload = json.dumps(data)

    headers_list = ['Content-Type: application/json']
    if hasattr(context, 'access_token'):
        headers_list.append(f'Authorization: Bearer {context.access_token}')

    if not endpoint.endswith('/'):
        endpoint += '/'

    cmd = [
        'curl',
        '--data', payload,
        '--request', 'POST',
        '--silent',
        '--write-out', '\\n%{http_code}',
        f'http://localhost:8000{endpoint}'
    ]

    for header in headers_list:
        cmd.extend(['--header', header])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=10
    )

    lines = result.stdout.strip().split('\n')
    context.response_status_code = int(lines[-1])
    context.response_body = '\n'.join(lines[:-1]) if len(lines) > 1 else ''

    try:
        context.response_json = json.loads(context.response_body) if context.response_body else {}
    except json.JSONDecodeError:
        context.response_json = {}


@then('the response contains field "{field}" with value {value:f}')
def step_response_field_numeric_value(context, field: str, value: float):
    """Verify the response contains a field with the expected numeric value."""
    assert field in context.response_json, \
        f"Expected field '{field}' in response, got: {context.response_json}"
    actual_value = float(context.response_json[field])
    assert actual_value == value, \
        f"Expected field '{field}' to be {value}, got {actual_value}"


@then('the response contains a list with at least {count:d} items')
def step_response_list_min_items(context, count: int):
    """Verify the response contains a list with at least the specified number of items."""
    assert isinstance(context.response_json, list), \
        f"Expected response to be a list, got: {type(context.response_json)}"
    assert len(context.response_json) >= count, \
        f"Expected at least {count} items in response, got {len(context.response_json)}"


@then('the response contains an error message about forecast limit')
def step_response_forecast_limit_error(context):
    """Verify the response contains an error message about the 7-day forecast limit."""
    assert context.response_status_code == 400, \
        f"Expected status code 400, got {context.response_status_code}"
    response_text = context.response_body.lower()
    assert 'forecast' in response_text or '7' in response_text or 'day' in response_text, \
        f"Expected error message about forecast limit, got: {context.response_body}"
