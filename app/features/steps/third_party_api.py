"""
Step definitions for third-party weather API integration.
"""
import json
import subprocess
from behave import given, when, then


@given('the third-party weather API is available')
def step_set_api_available(context):
    """Set the third-party API to available mode."""
    payload = json.dumps({"mode": "available"})
    cmd = [
        "curl",
        "--data", payload,
        "--header", "Content-Type: application/json",
        "--request", "POST",
        "--silent",
        "http://localhost:8000/api/test/set-mode/"
    ]
    subprocess.run(cmd, check=True, capture_output=True)


@given('the third-party weather API is unavailable')
def step_set_api_unavailable(context):
    """Set the third-party API to unavailable mode."""
    payload = json.dumps({"mode": "unavailable"})
    cmd = [
        "curl",
        "--data", payload,
        "--header", "Content-Type: application/json",
        "--request", "POST",
        "--silent",
        "http://localhost:8000/api/test/set-mode/"
    ]
    subprocess.run(cmd, check=True, capture_output=True)


@when('I trigger a fetch for {data_type} for "{city_name}"')
def step_trigger_fetch(context, data_type, city_name):
    """Trigger a weather data fetch from the third-party API."""
    if data_type == 'current weather':
        data_type_param = 'current'
    elif data_type == 'forecast':
        data_type_param = 'forecast'
    else:
        raise ValueError(f'Unknown data type: {data_type}')

    payload = json.dumps({
        "city_name": city_name,
        "data_type": data_type_param
    })

    cmd = [
        "curl",
        "--data", payload,
        "--header", "Content-Type: application/json",
        "--header", f"Authorization: Bearer {context.access_token}",
        "--request", "POST",
        "--silent",
        "--write-out", "\n%{http_code}",
        "http://localhost:8000/api/admin/fetch-weather/"
    ]

    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    output_lines = result.stdout.strip().split('\n')

    if len(output_lines) >= 2:
        context.response_body = '\n'.join(output_lines[:-1])
        context.response_status_code = int(output_lines[-1])
    else:
        context.response_status_code = int(output_lines[0])
        context.response_body = ""


@then('current weather data for "{city_name}" is stored')
def step_verify_current_weather_stored(context, city_name):
    """Verify that current weather data was stored in the database."""
    from weather.models import City, CurrentWeather

    city = City.objects.get(name=city_name)
    current_weather = CurrentWeather.objects.filter(city=city).first()

    assert current_weather is not None, f"No current weather data found for {city_name}"
    assert current_weather.temperature is not None
    assert current_weather.humidity is not None
    assert current_weather.pressure is not None
    assert current_weather.wind_speed is not None


@then('forecast data for "{city_name}" is stored')
def step_verify_forecast_stored(context, city_name):
    """Verify that forecast data was stored in the database."""
    from weather.models import City, WeatherForecast

    city = City.objects.get(name=city_name)
    forecasts = WeatherForecast.objects.filter(city=city)

    assert forecasts.exists(), f"No forecast data found for {city_name}"
    assert forecasts.count() >= 1, f"Expected at least 1 forecast entry for {city_name}"


@then('an error message is returned')
def step_verify_error_message(context):
    """Verify that an error message was returned."""
    assert context.response_body, "Expected an error message in the response body"
    response_data = json.loads(context.response_body)
    assert 'error' in response_data, "Expected 'error' field in response"
