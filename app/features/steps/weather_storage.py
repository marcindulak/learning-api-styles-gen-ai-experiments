"""
Step definitions for weather data storage.
"""
import json
import subprocess
from datetime import date, timedelta
from behave import given, when, then
from weather.models import City, CurrentWeather


@when('I store current weather for "{city_name}" with:')
def step_store_current_weather(context, city_name):
    """Store current weather data for a city."""
    weather_data = {'city_name': city_name}

    # Behave treats first row as headers
    if context.table.headings:
        key = context.table.headings[0]
        value = context.table.headings[1]
        weather_data[key] = float(value)

    # Add remaining rows
    for row in context.table:
        key = row.cells[0]
        value = row.cells[1]
        weather_data[key] = float(value)

    payload = json.dumps(weather_data)

    curl_command = [
        "curl",
        "-s",
        "--data", payload,
        "--header", "Content-Type: application/json",
        "--request", "POST",
        "--write-out", "\n%{http_code}",
    ]

    if hasattr(context, 'access_token') and context.access_token:
        curl_command.append("--header")
        curl_command.append(f"Authorization: Bearer {context.access_token}")

    curl_command.append("http://localhost:8000/api/weather/current/")

    result = subprocess.run(
        curl_command,
        capture_output=True,
        text=True
    )

    output_lines = result.stdout.strip().split('\n')
    context.response_status_code = int(output_lines[-1])
    context.response_body = '\n'.join(output_lines[:-1]) if len(output_lines) > 1 else ''


@given('current weather data exists for "{city_name}"')
def step_current_weather_exists(context, city_name):
    """Create current weather data for a city."""
    city = City.objects.create(
        name=city_name,
        country="Test Country",
        region="Test Region",
        timezone="UTC",
        latitude=0.0,
        longitude=0.0
    )
    CurrentWeather.objects.create(
        city=city,
        temperature=20.0,
        humidity=65.0,
        pressure=1012.0,
        wind_speed=3.5
    )


@then('the response contains weather data')
def step_response_contains_weather_data(context):
    """Verify that the response contains weather data fields."""
    response_data = json.loads(context.response_body)

    # Check if it's a paginated response (DRF pagination)
    if 'results' in response_data:
        assert len(response_data['results']) > 0, "Response results list is empty"
        weather_entry = response_data['results'][0]
    # Check if it's a list (non-paginated)
    elif isinstance(response_data, list):
        assert len(response_data) > 0, "Response list is empty"
        weather_entry = response_data[0]
    else:
        weather_entry = response_data

    # Verify weather data fields exist
    assert 'temperature' in weather_entry, f"Response missing temperature field. Response: {response_data}"
    assert 'humidity' in weather_entry, f"Response missing humidity field. Response: {response_data}"
    assert 'pressure' in weather_entry, f"Response missing pressure field. Response: {response_data}"
    assert 'wind_speed' in weather_entry, f"Response missing wind_speed field. Response: {response_data}"


@when('I store a 5-day forecast for "{city_name}"')
def step_store_5day_forecast(context, city_name):
    """Store a 5-day forecast for a city."""
    # Create 5 forecast entries
    forecasts = []
    for i in range(1, 6):
        forecast_date = date.today() + timedelta(days=i)
        forecasts.append({
            'city_name': city_name,
            'forecast_date': str(forecast_date),
            'temperature': 20.0 + i,
            'humidity': 60.0,
            'pressure': 1013.0,
            'wind_speed': 5.0
        })

    # Store each forecast
    for forecast_data in forecasts:
        payload = json.dumps(forecast_data)

        curl_command = [
            "curl",
            "-s",
            "--data", payload,
            "--header", "Content-Type: application/json",
            "--request", "POST",
            "--write-out", "\n%{http_code}",
        ]

        if hasattr(context, 'access_token') and context.access_token:
            curl_command.append("--header")
            curl_command.append(f"Authorization: Bearer {context.access_token}")

        curl_command.append("http://localhost:8000/api/weather/forecast/")

        result = subprocess.run(
            curl_command,
            capture_output=True,
            text=True
        )

        output_lines = result.stdout.strip().split('\n')
        status_code = int(output_lines[-1])

        # Store the last response
        context.response_status_code = status_code
        context.response_body = '\n'.join(output_lines[:-1]) if len(output_lines) > 1 else ''


@when('I store a forecast for "{city_name}" for {days:d} days from now')
def step_store_forecast_for_days(context, city_name, days):
    """Store a forecast for a specific number of days in the future."""
    forecast_date = date.today() + timedelta(days=days)

    forecast_data = {
        'city_name': city_name,
        'forecast_date': str(forecast_date),
        'temperature': 25.0,
        'humidity': 70.0,
        'pressure': 1015.0,
        'wind_speed': 4.5
    }

    payload = json.dumps(forecast_data)

    curl_command = [
        "curl",
        "-s",
        "--data", payload,
        "--header", "Content-Type: application/json",
        "--request", "POST",
        "--write-out", "\n%{http_code}",
    ]

    if hasattr(context, 'access_token') and context.access_token:
        curl_command.append("--header")
        curl_command.append(f"Authorization: Bearer {context.access_token}")

    curl_command.append("http://localhost:8000/api/weather/forecast/")

    result = subprocess.run(
        curl_command,
        capture_output=True,
        text=True
    )

    output_lines = result.stdout.strip().split('\n')
    context.response_status_code = int(output_lines[-1])
    context.response_body = '\n'.join(output_lines[:-1]) if len(output_lines) > 1 else ''
