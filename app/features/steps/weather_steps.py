"""
Step definitions for weather data features.
"""
from behave import given, when, then
from datetime import date, timedelta
from django.test import Client
from weather.models import City, WeatherRecord, Forecast
import json

@given('weather records exist for "{city_name}"')
def step_weather_records_exist(context, city_name):
    """Create weather records for a city."""
    city = City.objects.get(name=city_name)
    base_date = date.today()
    for i in range(7):
        WeatherRecord.objects.create(
            city=city,
            recorded_at=base_date - timedelta(days=i),
            temperature=20.0 + i,
            feels_like=19.0 + i,
            humidity=50 + i,
            wind_speed=5.0 + i,
            wind_direction=180,
            pressure=1013 + i,
            precipitation=0.0,
            uv_index=5,
            visibility=10.0,
            cloud_cover=50,
            description='Test'
        )


@given('weather records exist for the last 7 days')
def step_weather_records_last_7_days(context):
    """Create 7 days of weather records."""
    city = City.objects.first() or City.objects.create(
        name='Test City',
        country='Test Country',
        region='Test',
        timezone='UTC',
        latitude=0.0,
        longitude=0.0
    )
    base_date = date.today()
    for i in range(7):
        WeatherRecord.objects.create(
            city=city,
            recorded_at=base_date - timedelta(days=i),
            temperature=20.0,
            feels_like=19.0,
            humidity=50,
            wind_speed=5.0,
            wind_direction=180,
            pressure=1013,
            precipitation=0.0,
            uv_index=5,
            visibility=10.0,
            cloud_cover=50,
            description='Test'
        )


@given('7-day forecasts exist for "{city_name}"')
def step_forecasts_exist(context, city_name):
    """Create 7-day forecasts for a city."""
    city = City.objects.get(name=city_name)
    for i in range(1, 8):
        Forecast.objects.create(
            city=city,
            forecast_date=date.today() + timedelta(days=i),
            temperature_high=25.0 + i,
            temperature_low=15.0 + i,
            humidity=50 + i,
            wind_speed=5.0 + i,
            precipitation_probability=20 + i * 5,
            description='Test'
        )


@when('I request weather records for "{city_name}"')
def step_request_weather_records(context, city_name):
    """Request weather records for a city."""
    if not hasattr(context, 'client'):
        context.client = Client()
    city = City.objects.get(name=city_name)
    context.response = context.client.get(f'/api/weather-records/?city={city.uuid}')


@when('I request weather records from {days_ago:d} days ago to today')
def step_request_records_date_range(context, days_ago):
    """Request weather records for a date range."""
    if not hasattr(context, 'client'):
        context.client = Client()
    date_from = (date.today() - timedelta(days=days_ago)).isoformat()
    date_to = date.today().isoformat()
    context.response = context.client.get(
        f'/api/weather-records/?date_from={date_from}&date_to={date_to}'
    )


@when('I request forecasts for "{city_name}"')
def step_request_forecasts(context, city_name):
    """Request forecasts for a city."""
    if not hasattr(context, 'client'):
        context.client = Client()
    city = City.objects.get(name=city_name)
    context.response = context.client.get(f'/api/forecasts/?city={city.uuid}')


@when('I try to create a forecast for {days:d} days from now')
def step_create_forecast_future(context, days):
    """Try to create a forecast for future date."""
    if not hasattr(context, 'client'):
        context.client = Client()
    city = City.objects.first()
    forecast_date = (date.today() + timedelta(days=days)).isoformat()
    data = {
        'city': str(city.uuid),
        'forecast_date': forecast_date,
        'temperature_high': 25.0,
        'temperature_low': 15.0,
        'humidity': 50,
        'wind_speed': 5.0,
        'precipitation_probability': 20,
        'description': 'Test'
    }
    context.response = context.client.post(
        '/api/forecasts/',
        data=json.dumps(data),
        content_type='application/json'
    )


@when('I create a weather record for "{city_name}"')
def step_create_weather_record(context, city_name):
    """Create a weather record."""
    if not hasattr(context, 'client'):
        context.client = Client()
    city = City.objects.get(name=city_name)
    data = {
        'city': str(city.uuid),
        'recorded_at': date.today().isoformat(),
        'temperature': 20.0,
        'feels_like': 19.0,
        'humidity': 50,
        'wind_speed': 5.0,
        'wind_direction': 180,
        'pressure': 1013,
        'precipitation': 0.0,
        'uv_index': 5,
        'visibility': 10.0,
        'cloud_cover': 50,
        'description': 'Test'
    }
    context.response = context.client.post(
        '/api/weather-records/',
        data=json.dumps(data),
        content_type='application/json'
    )


@when('I try to create a forecast with forecast_date {days:d} days ahead')
def step_try_create_forecast_beyond_limit(context, days):
    """Try to create forecast beyond 7 days."""
    if not hasattr(context, 'client'):
        context.client = Client()
    city = City.objects.first()
    forecast_date = (date.today() + timedelta(days=days)).isoformat()
    data = {
        'city': str(city.uuid),
        'forecast_date': forecast_date,
        'temperature_high': 25.0,
        'temperature_low': 15.0,
        'humidity': 50,
        'wind_speed': 5.0,
        'precipitation_probability': 20,
        'description': 'Test'
    }
    context.response = context.client.post(
        '/api/forecasts/',
        data=json.dumps(data),
        content_type='application/json'
    )


@then('I get weather data with temperature readings')
def step_verify_weather_data(context):
    """Verify weather data is returned."""
    assert context.response.status_code == 200
    data = context.response.json()
    results = data.get('results', [])
    assert len(results) > 0
    assert 'temperature' in results[0]


@then('I get weather data for the requested period')
def step_verify_date_range_data(context):
    """Verify weather data for date range."""
    assert context.response.status_code == 200
    data = context.response.json()
    results = data.get('results', [])
    assert len(results) > 0


@then('I get {count:d} forecast entries')
def step_verify_forecast_count(context, count):
    """Verify forecast count."""
    assert context.response.status_code == 200
    data = context.response.json()
    results = data.get('results', [])
    assert len(results) == count


@then('each forecast has temperature high and low')
def step_verify_forecast_fields(context):
    """Verify forecasts have required fields."""
    data = context.response.json()
    results = data.get('results', [])
    for forecast in results:
        assert 'temperature_high' in forecast
        assert 'temperature_low' in forecast


@then('I get a 400 Bad Request error')
def step_verify_400_error(context):
    """Verify 400 response."""
    assert context.response.status_code == 400


@then('the error mentions "7 days"')
def step_error_mentions_7_days(context):
    """Verify error message mentions 7 days."""
    data = context.response.json()
    error_text = str(data).lower()
    assert '7' in error_text or 'day' in error_text


@then('the record contains')
def step_verify_record_fields(context):
    """Verify record contains required fields."""
    assert context.response.status_code == 201
    data = context.response.json()
    for row in context.table:
        field = row['field']
        assert field in data


@then('the API validation rejects it')
def step_api_rejects(context):
    """Verify API rejects the request."""
    assert context.response.status_code in [400, 422]


@then('the response status is 400')
def step_response_is_400(context):
    """Verify response status is 400."""
    assert context.response.status_code == 400
