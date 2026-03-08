"""
Step definitions for GraphQL API.
"""
import json
import subprocess
from datetime import date, timedelta

from behave import given, then, when

from weather.models import City, CurrentWeather, WeatherForecast




@given('current weather data exists for both "{city1}" and "{city2}"')
def step_create_current_weather_multiple(context, city1, city2):
    """Create current weather data for multiple cities."""
    for city_name in [city1, city2]:
        city, _ = City.objects.get_or_create(
            name=city_name,
            defaults={
                'country': 'Test Country',
                'latitude': 0.0,
                'longitude': 0.0,
            }
        )
        CurrentWeather.objects.create(
            city=city,
            temperature=20.0,
            humidity=60.0,
            pressure=1013.0,
            wind_speed=5.0,
        )


@when('I execute a GraphQL query for current weather in "{city_name}" requesting "{field1}" and "{field2}"')
def step_execute_graphql_current_weather_selective(context, city_name, field1, field2):
    """Execute GraphQL query for current weather with selective fields."""
    query = f'''
    {{
        currentWeather(cityName: "{city_name}") {{
            {field1}
            {field2}
        }}
    }}
    '''
    graphql_payload = json.dumps({'query': query})

    result = subprocess.run(
        [
            "curl",
            "--data", graphql_payload,
            "--header", "Content-Type: application/json",
            "--request", "POST",
            "--silent",
            "--output", "/dev/null",
            "--write-out", "%{http_code}",
            "http://localhost:8000/graphql"
        ],
        capture_output=True,
        text=True
    )
    context.response_status_code = int(result.stdout)

    result_with_body = subprocess.run(
        [
            "curl",
            "--data", graphql_payload,
            "--header", "Content-Type: application/json",
            "--request", "POST",
            "--silent",
            "http://localhost:8000/graphql"
        ],
        capture_output=True,
        text=True
    )
    context.response_body = result_with_body.stdout


@when('I execute a GraphQL query for forecasts in "{city_name}" for the next {days:d} days')
def step_execute_graphql_forecast_with_limit(context, city_name, days):
    """Execute GraphQL query for forecasts with date limit."""
    query = f'''
    {{
        forecasts(cityName: "{city_name}", days: {days}) {{
            forecastDate
            temperature
        }}
    }}
    '''
    graphql_payload = json.dumps({'query': query})

    result = subprocess.run(
        [
            "curl",
            "--data", graphql_payload,
            "--header", "Content-Type: application/json",
            "--request", "POST",
            "--silent",
            "--output", "/dev/null",
            "--write-out", "%{http_code}",
            "http://localhost:8000/graphql"
        ],
        capture_output=True,
        text=True
    )
    context.response_status_code = int(result.stdout)

    result_with_body = subprocess.run(
        [
            "curl",
            "--data", graphql_payload,
            "--header", "Content-Type: application/json",
            "--request", "POST",
            "--silent",
            "http://localhost:8000/graphql"
        ],
        capture_output=True,
        text=True
    )
    context.response_body = result_with_body.stdout


@when('I execute a GraphQL query requesting weather for both "{city1}" and "{city2}"')
def step_execute_graphql_multiple_cities(context, city1, city2):
    """Execute GraphQL query requesting weather for multiple cities."""
    query = f'''
    {{
        city1: currentWeather(cityName: "{city1}") {{
            temperature
            humidity
        }}
        city2: currentWeather(cityName: "{city2}") {{
            temperature
            humidity
        }}
    }}
    '''
    graphql_payload = json.dumps({'query': query})

    result = subprocess.run(
        [
            "curl",
            "--data", graphql_payload,
            "--header", "Content-Type: application/json",
            "--request", "POST",
            "--silent",
            "--output", "/dev/null",
            "--write-out", "%{http_code}",
            "http://localhost:8000/graphql"
        ],
        capture_output=True,
        text=True
    )
    context.response_status_code = int(result.stdout)

    result_with_body = subprocess.run(
        [
            "curl",
            "--data", graphql_payload,
            "--header", "Content-Type: application/json",
            "--request", "POST",
            "--silent",
            "http://localhost:8000/graphql"
        ],
        capture_output=True,
        text=True
    )
    context.response_body = result_with_body.stdout


@then('the GraphQL response contains "{field1}" and "{field2}" for "{city_name}"')
def step_verify_graphql_response_fields(context, field1, field2, city_name):
    """Verify GraphQL response contains specific fields."""
    response_data = json.loads(context.response_body)
    assert 'data' in response_data, f"No data in response: {response_data}"
    assert 'currentWeather' in response_data['data'], f"No currentWeather in response: {response_data}"
    current_weather = response_data['data']['currentWeather']
    assert current_weather is not None, f"currentWeather is null"
    assert field1 in current_weather, f"Field '{field1}' not in response: {current_weather}"
    assert field2 in current_weather, f"Field '{field2}' not in response: {current_weather}"


@then('the GraphQL response contains exactly {count:d} forecast entries')
def step_verify_graphql_forecast_count(context, count):
    """Verify GraphQL response contains exact number of forecast entries."""
    response_data = json.loads(context.response_body)
    assert 'data' in response_data, f"No data in response: {response_data}"
    assert 'forecasts' in response_data['data'], f"No forecasts in response: {response_data}"
    forecasts = response_data['data']['forecasts']
    assert len(forecasts) == count, f"Expected {count} forecasts, got {len(forecasts)}: {forecasts}"


@then('the GraphQL response contains data for both cities')
def step_verify_graphql_multiple_cities(context):
    """Verify GraphQL response contains data for both cities."""
    response_data = json.loads(context.response_body)
    assert 'data' in response_data, f"No data in response: {response_data}"
    assert 'city1' in response_data['data'], f"No city1 in response: {response_data}"
    assert 'city2' in response_data['data'], f"No city2 in response: {response_data}"
    assert response_data['data']['city1'] is not None, "city1 data is null"
    assert response_data['data']['city2'] is not None, "city2 data is null"
