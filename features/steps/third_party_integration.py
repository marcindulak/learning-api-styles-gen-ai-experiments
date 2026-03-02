"""Step definitions for third-party weather API integration."""

import json
import subprocess

from behave import given, then

from src.weather.models import City, CurrentWeather, WeatherForecast


@given('the third-party weather API is available')
def step_third_party_api_available(context):
    """Set test mode to simulate available API."""
    payload = json.dumps({'test_mode': 'available'})
    subprocess.run(
        [
            'curl',
            '--data', payload,
            '--header', 'Content-Type: application/json',
            '--request', 'POST',
            '--silent',
            'http://localhost:8000/api/test/set-mode/'
        ],
        capture_output=True,
        timeout=5
    )
    context.weather_api_test_mode = 'available'


@given('the third-party weather API is unavailable')
def step_third_party_api_unavailable(context):
    """Set test mode to simulate unavailable API."""
    payload = json.dumps({'test_mode': 'unavailable'})
    subprocess.run(
        [
            'curl',
            '--data', payload,
            '--header', 'Content-Type: application/json',
            '--request', 'POST',
            '--silent',
            'http://localhost:8000/api/test/set-mode/'
        ],
        capture_output=True,
        timeout=5
    )
    context.weather_api_test_mode = 'unavailable'


@then('weather data for "{city_name}" is stored in the database')
def step_weather_data_stored(context, city_name: str):
    """Verify current weather data is stored in the database."""
    city = City.objects.get(name=city_name)
    weather_data = CurrentWeather.objects.filter(city=city)
    assert weather_data.exists(), f"No weather data found for {city_name}"


@then('forecast data for "{city_name}" is stored in the database')
def step_forecast_data_stored(context, city_name: str):
    """Verify forecast data is stored in the database."""
    city = City.objects.get(name=city_name)
    forecast_data = WeatherForecast.objects.filter(city=city)
    assert forecast_data.exists(), f"No forecast data found for {city_name}"


@then('the response contains an error message about API unavailability')
def step_response_contains_api_error(context):
    """Verify the response contains an error about API unavailability."""
    assert 'error' in context.response_json, \
        f"Expected 'error' field in response, got: {context.response_json}"
    error_message = context.response_json['error'].lower()
    assert 'unavailable' in error_message or 'api' in error_message, \
        f"Expected API unavailability error, got: {context.response_json['error']}"
