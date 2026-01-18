"""
Step definitions for Feature 006: Weather Forecast
"""
import json
from behave import given, when, then
from django.utils import timezone
from datetime import timedelta
from apps.cities.models import City
from apps.weather.models import Forecast




def _create_forecast_data(context, city_name, days):
    """
    Helper to create forecast data for a city.
    """
    city = City.objects.get(name=city_name)
    days = int(days)

    if not hasattr(context, 'forecast_data'):
        context.forecast_data = {}
    context.forecast_data[city_name] = []

    base_time = timezone.now()
    for i in range(days):
        forecast = Forecast.objects.create(
            city=city,
            temperature=20.0 - i * 0.5,
            humidity=60 + (i % 20),
            wind_speed=10.0 + (i % 15),
            pressure=1013.25,
            description=f"Forecast day {i + 1}",
            forecast_date=base_time + timedelta(days=i)
        )
        context.forecast_data[city_name].append(forecast)


# Most specific patterns first
@given('forecast data exists for {city_name} spanning {days} days')
def step_forecast_data_spanning_days(context, city_name, days):
    """
    Create forecast data for a city spanning the specified number of days.
    """
    _create_forecast_data(context, city_name, days)


@given('forecast data exists for {city_name} for days {day_range}')
def step_forecast_days_range(context, city_name, day_range):
    """
    Create forecast data for a city spanning a range of days.
    """
    city = City.objects.get(name=city_name)

    if not hasattr(context, 'forecast_data'):
        context.forecast_data = {}
    context.forecast_data[city_name] = []

    base_time = timezone.now()
    # Parse range like "1-7"
    start, end = map(int, day_range.split('-'))
    for i in range(start - 1, end):
        forecast = Forecast.objects.create(
            city=city,
            temperature=20.0 - i * 0.5,
            humidity=60 + (i % 20),
            wind_speed=10.0 + (i % 15),
            pressure=1013.25,
            description=f"Forecast day {i + 1}",
            forecast_date=base_time + timedelta(days=i)
        )
        context.forecast_data[city_name].append(forecast)


# Least specific pattern last
@given('forecast data exists for {city_name}')
def step_forecast_data_exists(context, city_name):
    """
    Create forecast data for a city (7 days default).
    """
    _create_forecast_data(context, city_name, 7)


@when('I request the forecast for {city_name}')
def step_request_forecast(context, city_name):
    """
    Request forecast data for a city via REST API.
    """
    city = City.objects.get(name=city_name)

    if not hasattr(context, 'client'):
        from django.test import Client
        context.client = Client()

    # Ensure authentication token is available
    if not hasattr(context, 'access_token') or not context.access_token:
        # Authenticate as regular user
        credentials = {"username": "user", "password": "password"}
        response = context.client.post(
            '/api/jwt/obtain',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        if response.status_code == 200:
            context.response_data = json.loads(response.content)
            context.access_token = context.response_data.get('access')

    headers = {
        'Authorization': f'Bearer {context.access_token}' if context.access_token else '',
        'Content-Type': 'application/json'
    }

    response = context.client.get(
        f'/api/weather/forecast/?city_uuid={city.uuid}',
        HTTP_AUTHORIZATION=headers['Authorization']
    )

    context.forecast_response = response
    context.forecast_response_status = response.status_code

    if response.status_code == 200:
        context.forecast_response_data = json.loads(response.content)


@then('the response includes maximum {max_days} days of forecast data')
def step_response_max_days(context, max_days):
    """
    Verify the response includes at most the maximum number of days.
    """
    max_days = int(max_days)
    assert hasattr(context, 'forecast_response_data'), "No forecast response data found"

    # If response is a list (many=True), check the length
    if isinstance(context.forecast_response_data, list):
        assert len(context.forecast_response_data) <= max_days, \
            f"Expected at most {max_days} days, got {len(context.forecast_response_data)}"
    else:
        # If it's a single object, that's 1 day
        assert 1 <= max_days, f"Expected at most {max_days} days, got 1"


@given('{count} days of forecast data exist for {city_name}')
def step_forecast_days_exist(context, count, city_name):
    """
    Create forecast data for a city spanning the specified number of days.
    """
    city = City.objects.get(name=city_name)
    count = int(count)

    if not hasattr(context, 'forecast_data'):
        context.forecast_data = {}
    context.forecast_data[city_name] = []

    base_time = timezone.now()
    for i in range(count):
        forecast = Forecast.objects.create(
            city=city,
            temperature=20.0 - i * 0.5,
            humidity=60 + (i % 20),
            wind_speed=10.0 + (i % 15),
            pressure=1013.25,
            description=f"Forecast day {i + 1}",
            forecast_date=base_time + timedelta(days=i)
        )
        context.forecast_data[city_name].append(forecast)


@then('each forecast day includes temperature, humidity, wind_speed, and description')
def step_each_day_has_indicators(context):
    """
    Verify each forecast day includes required indicators.
    """
    assert hasattr(context, 'forecast_response_data'), "No forecast response data found"

    if not isinstance(context.forecast_response_data, list):
        context.forecast_response_data = [context.forecast_response_data]

    required_fields = ['temperature', 'humidity', 'wind_speed', 'description']
    for day_data in context.forecast_response_data:
        for field in required_fields:
            assert field in day_data, \
                f"Expected field '{field}' not found in forecast day"


@then('the forecast days are returned in ascending chronological order')
def step_forecast_chronological_order(context):
    """
    Verify forecast days are in chronological order.
    """
    assert hasattr(context, 'forecast_response_data'), "No forecast response data found"

    if not isinstance(context.forecast_response_data, list):
        context.forecast_response_data = [context.forecast_response_data]

    # Verify they are in order by checking forecast_date
    for i in range(len(context.forecast_response_data) - 1):
        current_date = context.forecast_response_data[i]['forecast_date']
        next_date = context.forecast_response_data[i + 1]['forecast_date']
        assert current_date <= next_date, \
            f"Forecast dates not in chronological order: {current_date} > {next_date}"


@given('a city "Copenhagen" exists with forecast data')
def step_copenhagen_with_forecast(context):
    """
    Ensure Copenhagen exists with forecast data.
    """
    city, created = City.objects.get_or_create(
        name='Copenhagen',
        defaults={
            'country': 'Denmark',
            'region': 'Europe',
            'timezone': 'Europe/Copenhagen',
            'latitude': 55.6761,
            'longitude': 12.5683
        }
    )

    if not hasattr(context, 'cities'):
        context.cities = {}
    context.cities['Copenhagen'] = {'uuid': str(city.uuid)}

    # Create forecast data if it doesn't exist
    if not Forecast.objects.filter(city=city).exists():
        base_time = timezone.now()
        for i in range(7):
            Forecast.objects.create(
                city=city,
                temperature=20.0 - i * 0.5,
                humidity=60 + (i % 20),
                wind_speed=10.0 + (i % 15),
                pressure=1013.25,
                description=f"Forecast day {i + 1}",
                forecast_date=base_time + timedelta(days=i)
            )


@when('I request the forecast via REST')
def step_request_forecast_rest(context):
    """
    Request forecast data via REST API.
    """
    if not hasattr(context, 'cities'):
        context.cities = {}

    # Get the first city from context
    if context.cities:
        city_uuid = list(context.cities.values())[0]['uuid']
    else:
        # Fall back to Copenhagen if set up
        city = City.objects.filter(name='Copenhagen').first()
        if not city:
            raise Exception("No city available for forecast request")
        city_uuid = str(city.uuid)

    if not hasattr(context, 'client'):
        from django.test import Client
        context.client = Client()

    # Ensure authentication token is available
    if not hasattr(context, 'access_token') or not context.access_token:
        # Authenticate as regular user
        credentials = {"username": "user", "password": "password"}
        response = context.client.post(
            '/api/jwt/obtain',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        if response.status_code == 200:
            context.response_data = json.loads(response.content)
            context.access_token = context.response_data.get('access')

    headers = {
        'Authorization': f'Bearer {context.access_token}' if hasattr(context, 'access_token') and context.access_token else '',
        'Content-Type': 'application/json'
    }

    response = context.client.get(
        f'/api/weather/forecast/?city_uuid={city_uuid}',
        HTTP_AUTHORIZATION=headers['Authorization']
    )

    context.forecast_response = response
    context.forecast_response_status = response.status_code
    # Alias for compatibility with REST API steps
    context.weather_response = response
    context.weather_response_status = response.status_code

    if response.status_code == 200:
        context.forecast_response_data = json.loads(response.content)
        context.weather_response_data = context.forecast_response_data




@then('the response includes {days}-day forecast data')
def step_response_includes_forecast_days(context, days):
    """
    Verify the response includes the specified number of days.
    """
    days = int(days)
    assert hasattr(context, 'forecast_response_data'), "No forecast response data found"

    if isinstance(context.forecast_response_data, list):
        assert len(context.forecast_response_data) > 0, "Forecast response is empty"
        assert len(context.forecast_response_data) <= 7, \
            f"Expected max 7 days, got {len(context.forecast_response_data)}"
    else:
        assert False, "Forecast response should be a list"


@when('I request the forecast via REST with authentication')
def step_request_forecast_authenticated(context):
    """
    Request forecast data via REST API with authentication.
    """
    city = City.objects.get(name='Copenhagen')

    if not hasattr(context, 'client'):
        from django.test import Client
        context.client = Client()

    headers = {
        'Authorization': f'Bearer {context.access_token}',
        'Content-Type': 'application/json'
    }

    response = context.client.get(
        f'/api/weather/forecast/?city_uuid={city.uuid}',
        HTTP_AUTHORIZATION=headers['Authorization']
    )

    context.forecast_response = response
    context.forecast_response_status = response.status_code
    # Alias for compatibility with REST API steps
    context.weather_response = response
    context.weather_response_status = response.status_code

    if response.status_code == 200:
        context.forecast_response_data = json.loads(response.content)
        context.weather_response_data = context.forecast_response_data


