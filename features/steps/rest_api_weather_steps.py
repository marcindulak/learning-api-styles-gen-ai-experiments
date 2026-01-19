"""
Step definitions for Feature 004: REST API Weather Indicators
"""
import json
from behave import given, when, then
from django.utils import timezone
from apps.cities.models import City
from apps.weather.models import Weather


@given("current weather data exists for {city_name}")
def step_current_weather_exists(context, city_name):
    """
    Ensure current weather data exists for a city.
    """
    city = City.objects.get(name=city_name)

    # Check if weather data already exists, if not create it
    weather = Weather.objects.filter(city=city).first()
    if not weather:
        weather = Weather.objects.create(
            city=city,
            temperature=15.5,
            humidity=65,
            wind_speed=10.2,
            pressure=1013.25,
            description="Partly cloudy",
            timestamp=timezone.now()
        )

    # Store weather data in context for later reference
    if not hasattr(context, 'weather_data'):
        context.weather_data = {}
    context.weather_data[city_name] = weather


@when("I request current weather for {city_name} via REST")
def step_request_weather_rest(context, city_name):
    """
    Request current weather data for a city via REST API.
    """
    city = City.objects.get(name=city_name)

    headers = {
        'Authorization': f'Bearer {context.access_token}',
        'Content-Type': 'application/json'
    }

    response = context.client.get(
        f'/api/weather/current/?city_uuid={city.uuid}',
        HTTP_AUTHORIZATION=headers['Authorization']
    )

    context.weather_response = response
    context.weather_response_status = response.status_code

    if response.status_code == 200:
        context.weather_response_data = json.loads(response.content)


@then("the response includes temperature, humidity, wind_speed, pressure, and description")
def step_response_includes_weather_indicators(context):
    """
    Verify the response includes all required weather indicators.
    """
    assert hasattr(context, 'weather_response_data'), "No weather response data found"

    required_fields = ['temperature', 'humidity', 'wind_speed', 'pressure', 'description']
    for field in required_fields:
        assert field in context.weather_response_data, \
            f"Expected field '{field}' not found in response"


@then("the response status is {status_code}")
def step_response_status(context, status_code):
    """
    Verify the response status code.
    """
    expected_status = int(status_code.split()[0])
    assert context.weather_response_status == expected_status, \
        f"Expected status {expected_status}, got {context.weather_response_status}"


@then("the response is valid JSON")
def step_response_is_json(context):
    """
    Verify the response is valid JSON.
    """
    try:
        assert hasattr(context, 'weather_response_data'), "No response data found"
        # If we got here, JSON parsing succeeded
    except (json.JSONDecodeError, AssertionError):
        raise AssertionError("Response is not valid JSON")


@then("the response contains city metadata")
def step_response_contains_city_metadata(context):
    """
    Verify the response includes city metadata.
    """
    assert hasattr(context, 'weather_response_data'), "No weather response data found"
    assert 'city' in context.weather_response_data, "City metadata not found in response"

    city_data = context.weather_response_data['city']
    required_city_fields = ['uuid', 'name', 'country']
    for field in required_city_fields:
        assert field in city_data, f"Expected city field '{field}' not found in response"


@given("no city named \"{city_name}\" exists")
def step_no_city_exists(context, city_name):
    """
    Ensure a city does not exist.
    """
    City.objects.filter(name=city_name).delete()


@given("no city named \"{city_name}\" exists in the system")
def step_no_city_exists_in_system(context, city_name):
    """
    Ensure a city does not exist in the system.
    """
    City.objects.filter(name=city_name).delete()


@when("I request current weather for {city_name} via REST with authentication")
def step_request_weather_authenticated(context, city_name):
    """
    Request current weather data for a city via REST API with authentication.
    """
    city = City.objects.get(name=city_name)

    headers = {
        'Authorization': f'Bearer {context.access_token}',
        'Content-Type': 'application/json'
    }

    response = context.client.get(
        f'/api/weather/current/?city_uuid={city.uuid}',
        HTTP_AUTHORIZATION=headers['Authorization']
    )

    context.weather_response = response
    context.weather_response_status = response.status_code

    if response.status_code == 200:
        context.weather_response_data = json.loads(response.content)


@then("the request succeeds with status {status_code}")
def step_request_succeeds_with_status(context, status_code):
    """
    Verify the request succeeded with the expected status.
    """
    expected_status = int(status_code)
    assert context.weather_response_status == expected_status, \
        f"Expected status {expected_status}, got {context.weather_response_status}"


@then("the request fails with a {status_code} {status_text} status")
def step_request_fails_with_status(context, status_code, status_text):
    """
    Verify the request failed with the expected status.
    """
    expected_status = int(status_code)
    assert context.weather_response_status == expected_status, \
        f"Expected status {expected_status} ({status_text}), got {context.weather_response_status}"


@given("a city \"{city_name}\" exists with weather data")
def step_city_exists_with_weather_data(context, city_name):
    """
    Ensure a city exists with current weather data.
    """
    city = City.objects.filter(name=city_name).first()
    if not city:
        city = City.objects.create(
            name=city_name,
            country="Test Country",
            region="Test Region",
            timezone="UTC",
            latitude=0.0,
            longitude=0.0
        )

    # Check if weather data already exists, if not create it
    weather = Weather.objects.filter(city=city).first()
    if not weather:
        weather = Weather.objects.create(
            city=city,
            temperature=15.5,
            humidity=65,
            wind_speed=10.2,
            pressure=1013.25,
            description="Partly cloudy",
            timestamp=timezone.now()
        )

    # Store in context for later reference
    if not hasattr(context, 'cities'):
        context.cities = {}
    context.cities[city_name] = {'uuid': str(city.uuid)}

    if not hasattr(context, 'weather_data'):
        context.weather_data = {}
    context.weather_data[city_name] = weather


@given("a city \"{city_name}\" exists in the system")
def step_city_exists_in_system(context, city_name):
    """
    Ensure a city exists in the system.
    """
    city = City.objects.filter(name=city_name).first()
    if not city:
        city = City.objects.create(
            name=city_name,
            country="Test Country",
            region="Test Region",
            timezone="UTC",
            latitude=0.0,
            longitude=0.0
        )

    # Store in context for later reference
    if not hasattr(context, 'cities'):
        context.cities = {}
    context.cities[city_name] = {'uuid': str(city.uuid), 'name': city_name}


@given("weather data is available for \"{city_name}\"")
def step_weather_data_available(context, city_name):
    """
    Ensure weather data is available for a city.
    """
    city = City.objects.get(name=city_name)

    # Check if weather data already exists, if not create it
    weather = Weather.objects.filter(city=city).first()
    if not weather:
        weather = Weather.objects.create(
            city=city,
            temperature=15.5,
            humidity=65,
            wind_speed=10.2,
            pressure=1013.25,
            description="Partly cloudy",
            timestamp=timezone.now()
        )

    # Store in context
    if not hasattr(context, 'weather_data'):
        context.weather_data = {}
    context.weather_data[city_name] = weather


@when("the client sends a GET request to {endpoint}")
def step_client_sends_get_request(context, endpoint):
    """
    Send a GET request to the specified endpoint.
    """
    # Ensure we have an access token - get one if we don't
    if not hasattr(context, 'access_token') or not context.access_token:
        # Get token for admin user
        payload = {
            'username': 'admin',
            'password': 'admin',
        }
        token_response = context.client.post(
            '/api/jwt/obtain',
            data=json.dumps(payload),
            content_type='application/json',
        )
        if token_response.status_code == 200:
            token_data = json.loads(token_response.content)
            context.access_token = token_data.get('access')

    headers = {
        'Content-Type': 'application/json'
    }

    # Add authorization header
    auth_header = ''
    if hasattr(context, 'access_token') and context.access_token:
        auth_header = f'Bearer {context.access_token}'
        headers['Authorization'] = auth_header

    response = context.client.get(
        endpoint,
        HTTP_AUTHORIZATION=auth_header,
        follow=True
    )

    context.response = response
    context.response_status = response.status_code

    try:
        context.response_data = json.loads(response.content)
    except (json.JSONDecodeError, ValueError):
        context.response_data = None


@then("the system returns HTTP {status_code} {status_text}")
def step_system_returns_status(context, status_code, status_text):
    """
    Verify the system returns the expected HTTP status code.
    """
    expected_status = int(status_code)
    assert context.response_status == expected_status, \
        f"Expected HTTP {expected_status} {status_text}, got {context.response_status}"


@then("the response contains weather indicators (temperature, humidity, pressure, wind speed)")
def step_response_contains_weather_indicators_new(context):
    """
    Verify the response contains weather indicators.
    """
    assert hasattr(context, 'response_data'), "No response data found"
    assert context.response_data is not None, "Response data is not valid JSON"

    # Handle both direct fields and nested city object
    if isinstance(context.response_data, dict):
        # Check if it's a single weather object or a paginated result
        data = context.response_data
        if 'results' in data:
            # Paginated response
            assert len(data['results']) > 0, "No weather data in results"
            data = data['results'][0]

        required_fields = ['temperature', 'humidity', 'pressure', 'wind_speed']
        for field in required_fields:
            assert field in data, f"Expected field '{field}' not found in response"


@then("the response is in JSON format")
def step_response_is_json_format(context):
    """
    Verify the response is in JSON format.
    """
    assert hasattr(context, 'response_data'), "No response data found"
    assert context.response_data is not None, "Response is not valid JSON"


@then("the response contains an error message")
def step_response_contains_error_message(context):
    """
    Verify the response contains an error message.
    """
    assert hasattr(context, 'response_data'), "No response data found"

    # Check for error in response
    if context.response_data is None:
        # If JSON parsing failed, check the raw response
        assert len(context.response.content) > 0, "Response contains no error message"
    else:
        # Check for common error field names
        error_found = ('detail' in context.response_data or
                      'error' in context.response_data or
                      'message' in context.response_data)
        assert error_found, f"No error message found in response: {context.response_data}"
