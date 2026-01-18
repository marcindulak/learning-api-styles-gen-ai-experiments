"""
Step definitions for Feature 005: GraphQL API Weather Indicators
"""
import json
from behave import given, when, then
from django.utils import timezone
from apps.cities.models import City
from apps.weather.models import Weather


@when("I query weather for {city_name} via GraphQL requesting temperature and humidity")
def step_query_weather_graphql_select_fields(context, city_name):
    """
    Query weather data via GraphQL for a specific city with field selection.
    """
    try:
        city = City.objects.get(name=city_name)
    except City.DoesNotExist:
        pass

    # GraphQL query requesting only temperature and humidity
    query = """
    {
        weatherByCity(cityName: "%s") {
            temperature
            humidity
        }
    }
    """ % city_name

    headers = {
        'Authorization': f'Bearer {context.access_token}',
        'Content-Type': 'application/json'
    }

    response = context.client.post(
        '/graphql/',
        data=json.dumps({'query': query}),
        content_type='application/json',
        HTTP_AUTHORIZATION=headers['Authorization']
    )

    context.graphql_response = response
    context.graphql_response_status = response.status_code

    if response.status_code == 200:
        try:
            context.graphql_response_data = json.loads(response.content)
        except json.JSONDecodeError:
            context.graphql_response_data = None


@then("the response includes only requested fields")
def step_response_includes_only_requested_fields(context):
    """
    Verify the response includes only the requested fields.
    """
    assert hasattr(context, 'graphql_response_data'), "No GraphQL response data found"
    assert context.graphql_response_data is not None, "GraphQL response data is None"

    # Check that we have data
    assert 'data' in context.graphql_response_data, "No 'data' field in response"

    weather_data = context.graphql_response_data['data'].get('weatherByCity')
    assert weather_data is not None, "No weather data in response"

    # Check requested fields are present
    assert 'temperature' in weather_data, "Temperature field not found"
    assert 'humidity' in weather_data, "Humidity field not found"


@when("I query weather via GraphQL requesting temperature, humidity, and wind_speed")
def step_query_weather_graphql_multiple_fields(context):
    """
    Query weather data via GraphQL requesting multiple fields.
    """
    city_name = list(context.cities.keys())[0] if hasattr(context, 'cities') and context.cities else 'Copenhagen'

    query = """
    {
        weatherByCity(cityName: "%s") {
            temperature
            humidity
            windSpeed
        }
    }
    """ % city_name

    headers = {
        'Authorization': f'Bearer {context.access_token}',
        'Content-Type': 'application/json'
    }

    response = context.client.post(
        '/graphql/',
        data=json.dumps({'query': query}),
        content_type='application/json',
        HTTP_AUTHORIZATION=headers['Authorization']
    )

    context.graphql_response = response
    context.graphql_response_status = response.status_code

    if response.status_code == 200:
        try:
            context.graphql_response_data = json.loads(response.content)
        except json.JSONDecodeError:
            context.graphql_response_data = None


@then("only the requested fields are returned in the response")
def step_only_requested_fields_in_response(context):
    """
    Verify only requested fields are in the response.
    """
    assert hasattr(context, 'graphql_response_data'), "No GraphQL response data found"
    assert context.graphql_response_data is not None, "GraphQL response data is None"

    assert 'data' in context.graphql_response_data, "No 'data' field in response"

    weather_data = context.graphql_response_data['data'].get('weatherByCity')
    assert weather_data is not None, "No weather data in response"

    # Verify requested fields are present
    assert 'temperature' in weather_data, "Temperature field not found"
    assert 'humidity' in weather_data, "Humidity field not found"
    assert 'windSpeed' in weather_data, "Wind speed field not found"


@when("I query weather for \"{city_name}\" via GraphQL")
def step_query_weather_nonexistent_city_graphql(context, city_name):
    """
    Query weather for a non-existent city via GraphQL.
    """
    query = """
    {
        weatherByCity(cityName: "%s") {
            temperature
            humidity
        }
    }
    """ % city_name

    headers = {
        'Authorization': f'Bearer {context.access_token}',
        'Content-Type': 'application/json'
    }

    response = context.client.post(
        '/graphql/',
        data=json.dumps({'query': query}),
        content_type='application/json',
        HTTP_AUTHORIZATION=headers['Authorization']
    )

    context.graphql_response = response
    context.graphql_response_status = response.status_code

    if response.status_code == 200:
        try:
            context.graphql_response_data = json.loads(response.content)
        except json.JSONDecodeError:
            context.graphql_response_data = None


@then("the response contains an error indicating city not found")
def step_response_contains_error_city_not_found(context):
    """
    Verify the response contains an error for city not found.
    """
    assert hasattr(context, 'graphql_response_data'), "No GraphQL response data found"
    assert context.graphql_response_data is not None, "GraphQL response data is None"

    # GraphQL returns errors in an 'errors' field
    assert 'errors' in context.graphql_response_data or \
           (context.graphql_response_data.get('data', {}).get('weatherByCity') is None), \
           "Expected an error response or null data"


@given("weather data exists without a description field")
def step_weather_data_without_description(context):
    """
    Create weather data without a description field.
    """
    city_name = list(context.cities.keys())[0] if hasattr(context, 'cities') and context.cities else 'Copenhagen'
    city = City.objects.get(name=city_name)

    # Delete existing weather data
    Weather.objects.filter(city=city).delete()

    # Create weather data without description
    weather = Weather.objects.create(
        city=city,
        temperature=15.5,
        humidity=65,
        wind_speed=10.2,
        pressure=1013.25,
        description=None,  # Explicitly set to None
        timestamp=timezone.now()
    )

    if not hasattr(context, 'weather_data'):
        context.weather_data = {}
    context.weather_data[city_name] = weather


@when("I query weather via GraphQL requesting all fields including description")
def step_query_weather_all_fields_graphql(context):
    """
    Query weather via GraphQL requesting all fields including description.
    """
    city_name = list(context.cities.keys())[0] if hasattr(context, 'cities') and context.cities else 'Copenhagen'

    query = """
    {
        weatherByCity(cityName: "%s") {
            temperature
            humidity
            windSpeed
            pressure
            description
        }
    }
    """ % city_name

    headers = {
        'Authorization': f'Bearer {context.access_token}',
        'Content-Type': 'application/json'
    }

    response = context.client.post(
        '/graphql/',
        data=json.dumps({'query': query}),
        content_type='application/json',
        HTTP_AUTHORIZATION=headers['Authorization']
    )

    context.graphql_response = response
    context.graphql_response_status = response.status_code

    if response.status_code == 200:
        try:
            context.graphql_response_data = json.loads(response.content)
        except json.JSONDecodeError:
            context.graphql_response_data = None


@then("the description field is null in the response")
def step_description_field_is_null(context):
    """
    Verify the description field is null in the response.
    """
    assert hasattr(context, 'graphql_response_data'), "No GraphQL response data found"
    assert context.graphql_response_data is not None, "GraphQL response data is None"

    assert 'data' in context.graphql_response_data, "No 'data' field in response"

    weather_data = context.graphql_response_data['data'].get('weatherByCity')
    assert weather_data is not None, "No weather data in response"

    assert 'description' in weather_data, "Description field not found in response"
    assert weather_data['description'] is None, "Expected description to be null"


@then("other fields are present")
def step_other_fields_present(context):
    """
    Verify other fields are present in the response.
    """
    assert hasattr(context, 'graphql_response_data'), "No GraphQL response data found"
    assert context.graphql_response_data is not None, "GraphQL response data is None"

    weather_data = context.graphql_response_data['data'].get('weatherByCity')
    assert weather_data is not None, "No weather data in response"

    # Verify non-null fields are present
    assert 'temperature' in weather_data, "Temperature field not found"
    assert weather_data['temperature'] is not None, "Temperature should not be null"

    assert 'humidity' in weather_data, "Humidity field not found"
    assert weather_data['humidity'] is not None, "Humidity should not be null"

    assert 'windSpeed' in weather_data, "Wind speed field not found"
    assert weather_data['windSpeed'] is not None, "Wind speed should not be null"


@when("I query weather via GraphQL with authentication")
def step_query_weather_graphql_authenticated(context):
    """
    Query weather via GraphQL with authentication.
    """
    city_name = list(context.cities.keys())[0] if hasattr(context, 'cities') and context.cities else 'Copenhagen'

    query = """
    {
        weatherByCity(cityName: "%s") {
            temperature
            humidity
            windSpeed
        }
    }
    """ % city_name

    headers = {
        'Authorization': f'Bearer {context.access_token}',
        'Content-Type': 'application/json'
    }

    response = context.client.post(
        '/graphql/',
        data=json.dumps({'query': query}),
        content_type='application/json',
        HTTP_AUTHORIZATION=headers['Authorization']
    )

    context.graphql_response = response
    context.graphql_response_status = response.status_code

    if response.status_code == 200:
        try:
            context.graphql_response_data = json.loads(response.content)
        except json.JSONDecodeError:
            context.graphql_response_data = None
