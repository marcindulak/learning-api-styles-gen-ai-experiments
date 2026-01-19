"""
Step definitions for Feature 004: GraphQL API for Weather Indicators
"""
import json
from behave import given, when, then
from django.utils import timezone
from apps.cities.models import City
from apps.weather.models import Weather


@given("a GraphQL endpoint is available")
def step_graphql_endpoint_available(context):
    """
    Verify that the GraphQL endpoint is available.
    """
    # The endpoint is available at /graphql/
    # We'll verify this by checking the client can make requests to it
    context.graphql_endpoint = '/graphql/'


@when("the client sends a GraphQL query requesting temperature and humidity for \"{city_name}\"")
def step_graphql_query_temperature_humidity(context, city_name):
    """
    Send a GraphQL query requesting only temperature and humidity for a city.
    """
    # Ensure we have an access token
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
    context.response_status = response.status_code  # Use response_status for compatibility with other steps

    if response.status_code == 200:
        try:
            context.response_data = json.loads(response.content)
            context.graphql_response_data = context.response_data
        except json.JSONDecodeError:
            context.graphql_response_data = None


@when("the client sends a GraphQL query with an invalid field name")
def step_graphql_query_invalid_field(context):
    """
    Send a GraphQL query with an invalid field name to test error handling.
    """
    # Ensure we have an access token
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

    # GraphQL query with an invalid field name
    city_name = "Copenhagen"
    query = """
    {
        weatherByCity(cityName: "%s") {
            temperature
            invalidFieldName
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
    context.response_status = response.status_code

    try:
        context.response_data = json.loads(response.content)
        context.graphql_response_data = context.response_data
    except json.JSONDecodeError:
        context.graphql_response_data = None


@then("the response contains only the requested fields (temperature and humidity)")
def step_response_only_requested_fields(context):
    """
    Verify the response contains only the requested fields (temperature and humidity).
    """
    # Use response_data which is set by the when step
    response_data = getattr(context, 'response_data', getattr(context, 'graphql_response_data', None))
    assert response_data is not None, "No response data found"

    # Check that we have data
    assert 'data' in response_data, "No 'data' field in response"

    weather_data = response_data['data'].get('weatherByCity')
    assert weather_data is not None, "No weather data in response"

    # Check requested fields are present
    assert 'temperature' in weather_data, "Temperature field not found"
    assert 'humidity' in weather_data, "Humidity field not found"

    # Verify that only the requested fields are in the response (no extra fields)
    allowed_fields = {'temperature', 'humidity', '__typename'}
    response_fields = set(weather_data.keys())
    extra_fields = response_fields - allowed_fields
    assert not extra_fields, f"Unexpected fields in response: {extra_fields}"


@then("the response is in JSON format with GraphQL structure")
def step_response_graphql_json_format(context):
    """
    Verify the response is in JSON format with proper GraphQL structure.
    """
    response_data = getattr(context, 'response_data', getattr(context, 'graphql_response_data', None))
    assert response_data is not None, "No response data found"

    # Verify GraphQL structure: should have 'data' or 'errors' key
    assert 'data' in response_data or 'errors' in response_data, \
        "Response does not have GraphQL structure (missing 'data' or 'errors')"


@then("the system returns a GraphQL error in the response")
def step_graphql_error_in_response(context):
    """
    Verify the response contains a GraphQL error.
    """
    response_data = getattr(context, 'response_data', getattr(context, 'graphql_response_data', None))
    assert response_data is not None, "No response data found"

    # GraphQL errors can be in the 'errors' field
    assert 'errors' in response_data, \
        "Expected 'errors' field in GraphQL error response"
    assert len(response_data['errors']) > 0, \
        "Expected at least one error in the errors field"


@then("no data is returned for that field")
def step_no_data_for_field(context):
    """
    Verify that no data is returned for the invalid field.
    """
    response_data = getattr(context, 'response_data', getattr(context, 'graphql_response_data', None))
    assert response_data is not None, "No response data found"

    # In GraphQL, errors prevent data from being returned
    # Either we have errors, or we have null data
    if 'errors' in response_data:
        # If there are errors, that's acceptable
        pass
    elif 'data' in response_data:
        # If there's data, it should be null due to the error
        assert response_data['data'] is None or \
               response_data['data'].get('weatherByCity') is None, \
               "Expected null data for invalid field"
