"""
Step definitions for REST API weather data access.
"""
import json
from datetime import date, timedelta
from behave import given, then
from weather.models import City, CurrentWeather, WeatherForecast


@then('the response contains fields {field_list}')
def step_response_contains_fields(context, field_list):
    """Verify that the response contains specified fields."""
    response_data = json.loads(context.response_body)

    # Parse field list (format: "field1", "field2", "field3")
    fields = [f.strip().strip('"\'') for f in field_list.split(',')]

    for field in fields:
        assert field in response_data, f"Response missing field: {field}. Response: {response_data}"


@given('forecast data exists for "{city_name}" for the next {days:d} days')
def step_forecast_data_exists(context, city_name, days):
    """Create forecast data for a city for the next N days."""
    city = City.objects.create(
        name=city_name,
        country="Test Country",
        region="Test Region",
        timezone="UTC",
        latitude=0.0,
        longitude=0.0
    )

    # Create forecast entries for each day
    for i in range(1, days + 1):
        forecast_date = date.today() + timedelta(days=i)
        WeatherForecast.objects.create(
            city=city,
            forecast_date=forecast_date,
            temperature=20.0 + i,
            humidity=60.0,
            pressure=1013.0,
            wind_speed=5.0
        )


@then('the response contains forecast entries')
def step_response_contains_forecast_entries(context):
    """Verify that the response contains forecast entries."""
    response_data = json.loads(context.response_body)

    # Check if response is a list
    if isinstance(response_data, list):
        assert len(response_data) > 0, "Forecast response list is empty"
        forecast_entry = response_data[0]
    else:
        assert False, f"Expected list of forecast entries, got: {response_data}"

    # Verify forecast data fields exist
    assert 'forecast_date' in forecast_entry, f"Response missing forecast_date field. Response: {response_data}"
    assert 'temperature' in forecast_entry, f"Response missing temperature field. Response: {response_data}"
    assert 'humidity' in forecast_entry, f"Response missing humidity field. Response: {response_data}"


@given('weather data exists for multiple cities')
def step_weather_data_for_multiple_cities(context):
    """Create weather data for multiple cities."""
    cities = ['London', 'Paris', 'Tokyo']

    for city_name in cities:
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


@then('the response contains a list of cities')
def step_response_contains_list_of_cities(context):
    """Verify that the response contains a list of cities."""
    response_data = json.loads(context.response_body)

    # Check if it's a paginated response (DRF pagination)
    if 'results' in response_data:
        assert len(response_data['results']) > 0, "Response results list is empty"
        city_entry = response_data['results'][0]
    else:
        assert isinstance(response_data, list), f"Expected list response, got: {type(response_data)}"
        assert len(response_data) > 0, "Response list is empty"
        city_entry = response_data[0]

    # Verify city fields exist
    assert 'name' in city_entry, f"Response missing name field. Response: {response_data}"
