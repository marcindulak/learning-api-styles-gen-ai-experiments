"""Step definitions for REST API features."""

import json
import subprocess
from datetime import date, timedelta

from behave import given, then, when

from src.weather.models import City, CurrentWeather, WeatherForecast


@given('cities "{city_list}" exist')
def step_multiple_cities_exist(context, city_list: str):
    """Create multiple cities in the database."""
    city_names = [name.strip().strip('"') for name in city_list.split(',')]
    for city_name in city_names:
        if not City.objects.filter(name=city_name).exists():
            City.objects.create(
                name=city_name,
                country='Default Country',
                region='Default Region',
                timezone='UTC',
                latitude=0.0,
                longitude=0.0
            )


@given('current weather data exists for "{city_name}"')
def step_current_weather_exists(context, city_name: str):
    """Create current weather data for a city."""
    city = City.objects.get(name=city_name)

    if not CurrentWeather.objects.filter(city=city).exists():
        CurrentWeather.objects.create(
            city=city,
            temperature=18.5,
            humidity=70,
            pressure=1015,
            wind_speed=8.5,
            conditions='Sunny',
            timestamp='2026-03-01T12:00:00Z'
        )


@given('forecast data exists for "{city_name}" for the next 7 days')
def step_forecast_data_exists(context, city_name: str):
    """Create 7 days of forecast data for a city."""
    city = City.objects.get(name=city_name)

    # Clear existing forecasts for this city
    WeatherForecast.objects.filter(city=city).delete()

    # Create forecast for next 7 days
    today = date.today()
    for i in range(1, 8):
        forecast_date = today + timedelta(days=i)
        WeatherForecast.objects.create(
            city=city,
            forecast_date=forecast_date,
            temperature=15.0 + i,
            humidity=60 + i,
            pressure=1010 + i,
            wind_speed=5.0 + i,
            conditions=f'Condition {i}'
        )


@given('current weather data exists for all cities')
def step_current_weather_exists_all_cities(context):
    """Create current weather data for all cities."""
    cities = City.objects.all()
    created_count = 0
    for city in cities:
        if not CurrentWeather.objects.filter(city=city).exists():
            CurrentWeather.objects.create(
                city=city,
                temperature=20.0,
                humidity=65,
                pressure=1012,
                wind_speed=10.0,
                conditions='Clear',
                timestamp='2026-03-01T12:00:00Z'
            )
            created_count += 1
    # Verify data was created
    total_weather = CurrentWeather.objects.count()
    assert total_weather > 0, f"No weather data created. Cities: {cities.count()}, Created: {created_count}"




@then('the response contains a list with {count:d} items')
def step_response_list_exact_items(context, count: int):
    """Verify the response contains a list with exactly the specified number of items."""
    if isinstance(context.response_json, dict) and 'results' in context.response_json:
        actual_list = context.response_json['results']
    elif isinstance(context.response_json, list):
        actual_list = context.response_json
    else:
        raise AssertionError(f"Expected response to be a list or contain 'results', got: {type(context.response_json)}")

    assert len(actual_list) == count, \
        f"Expected exactly {count} items in response, got {len(actual_list)}"


@then('each forecast contains fields "{fields}"')
def step_each_forecast_contains_fields(context, fields: str):
    """Verify each forecast in the response contains the specified fields."""
    field_list = [f.strip().strip('"\'') for f in fields.split(',')]

    if isinstance(context.response_json, dict) and 'results' in context.response_json:
        forecasts = context.response_json['results']
    elif isinstance(context.response_json, list):
        forecasts = context.response_json
    else:
        raise AssertionError(f"Expected response to be a list or contain 'results', got: {type(context.response_json)}")

    for forecast in forecasts:
        for field in field_list:
            assert field in forecast, \
                f"Expected field '{field}' in forecast, got: {forecast}"
