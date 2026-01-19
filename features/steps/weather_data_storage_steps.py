"""
Step definitions for Feature 003: Weather Data Storage
"""
from behave import given, when, then
from django.utils import timezone
from datetime import timedelta
from apps.cities.models import City
from apps.weather.models import Weather


@when('I store weather data for {city_name} with temperature {temperature}, humidity {humidity}, wind_speed {wind_speed}, and timestamp')
def step_store_weather_data_simple(context, city_name, temperature, humidity, wind_speed):
    """
    Store weather data for a city with given indicators.
    """
    city = City.objects.get(name=city_name)

    weather = Weather.objects.create(
        city=city,
        temperature=float(temperature),
        humidity=int(humidity),
        wind_speed=float(wind_speed),
        timestamp=timezone.now()
    )

    # Store in context for later assertions
    if not hasattr(context, 'last_weather'):
        context.last_weather = {}
    context.last_weather[city_name] = weather


@then('the weather data is persisted in the database')
def step_weather_persisted(context):
    """
    Verify that weather data was persisted to the database.
    """
    # Check if we can retrieve the last weather record
    assert hasattr(context, 'last_weather') and context.last_weather, \
        "No weather data was stored"

    # Verify it exists in the database
    for city_name, weather in context.last_weather.items():
        fetched = Weather.objects.get(uuid=weather.uuid)
        assert fetched is not None, f"Weather record for {city_name} not found in database"


@then('the weather record has a reference to {city_name}')
def step_weather_has_city_reference(context, city_name):
    """
    Verify that weather record references the correct city.
    """
    assert hasattr(context, 'last_weather') and city_name in context.last_weather, \
        f"No weather data stored for {city_name}"

    weather = context.last_weather[city_name]
    assert weather.city.name == city_name, \
        f"Expected city {city_name}, got {weather.city.name}"


@when('I store {count} separate weather records for {city_name} with different timestamps')
def step_store_multiple_weather_records(context, count, city_name):
    """
    Store multiple weather records for a city with different timestamps.
    """
    city = City.objects.get(name=city_name)
    count = int(count)

    if not hasattr(context, 'multiple_weather'):
        context.multiple_weather = {}
    context.multiple_weather[city_name] = []

    # Create weather records with timestamps spread out
    base_time = timezone.now()
    for i in range(count):
        weather = Weather.objects.create(
            city=city,
            temperature=15.0 + i,
            humidity=60 + i,
            wind_speed=10.0 + i,
            timestamp=base_time - timedelta(hours=i)
        )
        context.multiple_weather[city_name].append(weather)


@then('all {count} records are stored in the database')
def step_all_records_stored(context, count):
    """
    Verify that all weather records were stored.
    """
    count = int(count)
    assert hasattr(context, 'multiple_weather'), "No multiple weather records were stored"

    # Get the city from first record
    for city_name, records in context.multiple_weather.items():
        assert len(records) == count, \
            f"Expected {count} records, got {len(records)}"

        # Verify all records exist in database
        for record in records:
            fetched = Weather.objects.get(uuid=record.uuid)
            assert fetched is not None, f"Record {record.uuid} not found in database"


@then('all records reference {city_name}')
def step_all_records_reference_city(context, city_name):
    """
    Verify that all weather records reference the correct city.
    """
    assert hasattr(context, 'multiple_weather') and city_name in context.multiple_weather, \
        f"No weather records found for {city_name}"

    for record in context.multiple_weather[city_name]:
        assert record.city.name == city_name, \
            f"Expected city {city_name}, got {record.city.name}"


@when('I store weather data with temperature, humidity, wind_speed, pressure, and description')
def step_store_weather_all_indicators(context):
    """
    Store weather data with all available indicators.
    """
    # Get Copenhagen city (should exist from given step)
    city = City.objects.get(name="Copenhagen")

    weather = Weather.objects.create(
        city=city,
        temperature=15.5,
        humidity=65,
        wind_speed=10.2,
        pressure=1013.25,
        description="Partly cloudy",
        timestamp=timezone.now()
    )

    if not hasattr(context, 'full_weather'):
        context.full_weather = {}
    context.full_weather['Copenhagen'] = weather


@then('all weather indicators are persisted')
def step_all_indicators_persisted(context):
    """
    Verify that all weather indicators were persisted.
    """
    assert hasattr(context, 'full_weather') and 'Copenhagen' in context.full_weather, \
        "No full weather data was stored"

    weather = context.full_weather['Copenhagen']
    fetched = Weather.objects.get(uuid=weather.uuid)

    assert fetched.temperature == 15.5
    assert fetched.humidity == 65
    assert fetched.wind_speed == 10.2
    assert fetched.pressure == 1013.25
    assert fetched.description == "Partly cloudy"


@then('the weather record is retrievable with all indicators')
def step_weather_retrievable_with_all_indicators(context):
    """
    Verify that weather record can be retrieved with all indicators intact.
    """
    assert hasattr(context, 'full_weather') and 'Copenhagen' in context.full_weather, \
        "No full weather data was stored"

    weather = context.full_weather['Copenhagen']
    fetched = Weather.objects.get(uuid=weather.uuid)

    assert fetched.temperature is not None
    assert fetched.humidity is not None
    assert fetched.wind_speed is not None
    assert fetched.pressure is not None
    assert fetched.description is not None


@given('multiple weather records exist for {city_name} spanning {days} days')
def step_multiple_weather_spanning_days(context, city_name, days):
    """
    Create multiple weather records spanning the given number of days.
    """
    city = City.objects.get(name=city_name)
    days = int(days)

    if not hasattr(context, 'historical_weather'):
        context.historical_weather = {}
    context.historical_weather[city_name] = []

    # Create one record per day
    base_time = timezone.now()
    for i in range(days):
        weather = Weather.objects.create(
            city=city,
            temperature=20.0 - i * 0.5,  # Temperature decreases over time
            humidity=60 + (i % 20),
            wind_speed=10.0 + (i % 15),
            timestamp=base_time - timedelta(days=i)
        )
        context.historical_weather[city_name].append(weather)


@when('I query historical weather data for {city_name}')
def step_query_historical_weather(context, city_name):
    """
    Query historical weather data for a city.
    """
    city = City.objects.get(name=city_name)

    # Query all weather records for this city, ordered by timestamp
    records = Weather.objects.filter(city=city).order_by('timestamp')

    context.query_results = {
        'city_name': city_name,
        'records': list(records)
    }


@then('I receive all historical records in chronological order')
def step_verify_chronological_order(context):
    """
    Verify that historical records are returned in chronological order.
    """
    assert hasattr(context, 'query_results'), "No query results available"

    records = context.query_results['records']
    assert len(records) > 0, "No records returned"

    # Verify they are in chronological order (oldest first)
    for i in range(len(records) - 1):
        assert records[i].timestamp <= records[i + 1].timestamp, \
            f"Records not in chronological order: {records[i].timestamp} > {records[i + 1].timestamp}"
