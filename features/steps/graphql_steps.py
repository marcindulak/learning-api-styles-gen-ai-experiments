"""
Step definitions for Feature 007: GraphQL Weather API
"""
from behave import when, then
import json


GRAPHQL_ENDPOINT = '/graphql'


def execute_graphql_query(context, query, variables=None):
    """Helper function to execute a GraphQL query."""
    payload = {'query': query}
    if variables:
        payload['variables'] = variables

    headers = {'content_type': 'application/json'}

    if hasattr(context, 'access_token') and context.access_token:
        headers['HTTP_AUTHORIZATION'] = f'Bearer {context.access_token}'

    context.response = context.client.post(
        GRAPHQL_ENDPOINT,
        data=json.dumps(payload),
        content_type='application/json',
        **{k: v for k, v in headers.items() if k != 'content_type'}
    )

    try:
        context.response_data = json.loads(context.response.content)
        context.graphql_data = context.response_data.get('data')
    except (json.JSONDecodeError, ValueError):
        context.response_data = None
        context.graphql_data = None


@when('I send a GraphQL query for all cities')
def step_graphql_query_all_cities(context):
    """Send a GraphQL query for all cities."""
    query = '''
    query {
        allCities {
            uuid
            name
            country
            region
            timezone
            latitude
            longitude
        }
    }
    '''
    execute_graphql_query(context, query)


@when('I send a GraphQL query for city "{city_name}" by UUID')
def step_graphql_query_city_by_uuid(context, city_name):
    """Send a GraphQL query for a specific city by UUID."""
    assert hasattr(context, 'city_uuids') and city_name in context.city_uuids, \
        f"City UUID for '{city_name}' not found"

    city_uuid = str(context.city_uuids[city_name])

    query = '''
    query($uuid: UUID!) {
        city(uuid: $uuid) {
            uuid
            name
            country
            region
            timezone
            latitude
            longitude
        }
    }
    '''
    execute_graphql_query(context, query, variables={'uuid': city_uuid})


@when('I send a GraphQL query for current weather of city "{city_name}"')
def step_graphql_query_current_weather(context, city_name):
    """Send a GraphQL query for current weather of a city."""
    assert hasattr(context, 'city_uuids') and city_name in context.city_uuids, \
        f"City UUID for '{city_name}' not found"

    city_uuid = str(context.city_uuids[city_name])

    query = '''
    query($cityUuid: UUID!) {
        currentWeather(cityUuid: $cityUuid) {
            uuid
            temperature
            humidity
            windSpeed
            pressure
            conditionCode
            condition
            timestamp
        }
    }
    '''
    execute_graphql_query(context, query, variables={'cityUuid': city_uuid})


@when('I send a GraphQL query for weather forecast of city "{city_name}"')
def step_graphql_query_forecast(context, city_name):
    """Send a GraphQL query for weather forecast of a city."""
    assert hasattr(context, 'city_uuids') and city_name in context.city_uuids, \
        f"City UUID for '{city_name}' not found"

    city_uuid = str(context.city_uuids[city_name])

    query = '''
    query($cityUuid: UUID!) {
        forecast(cityUuid: $cityUuid) {
            uuid
            forecastDate
            temperature
            humidity
            windSpeed
            condition
        }
    }
    '''
    execute_graphql_query(context, query, variables={'cityUuid': city_uuid})


@when('I send a GraphQL query for historical weather of city "{city_name}" on date "{date_str}"')
def step_graphql_query_historical(context, city_name, date_str):
    """Send a GraphQL query for historical weather of a city on a specific date."""
    assert hasattr(context, 'city_uuids') and city_name in context.city_uuids, \
        f"City UUID for '{city_name}' not found"

    city_uuid = str(context.city_uuids[city_name])

    query = '''
    query($cityUuid: UUID!, $date: Date!) {
        historicalWeather(cityUuid: $cityUuid, date: $date) {
            uuid
            date
            temperature
            humidity
            windSpeed
            condition
        }
    }
    '''
    execute_graphql_query(context, query, variables={'cityUuid': city_uuid, 'date': date_str})


@when('I send a GraphQL introspection query')
def step_graphql_introspection(context):
    """Send a GraphQL introspection query."""
    query = '''
    query {
        __schema {
            types {
                name
                kind
            }
            queryType {
                name
            }
        }
    }
    '''
    execute_graphql_query(context, query)


@then('the GraphQL response contains a list of cities')
def step_graphql_response_contains_city_list(context):
    """Check that the GraphQL response contains a list of cities."""
    assert context.graphql_data is not None, \
        f"GraphQL data is None. Response: {context.response_data}"
    assert 'allCities' in context.graphql_data, \
        f"'allCities' not found in GraphQL data: {context.graphql_data}"
    assert isinstance(context.graphql_data['allCities'], list), \
        f"'allCities' should be a list, got {type(context.graphql_data['allCities'])}"


@then('the GraphQL response contains city name "{city_name}"')
def step_graphql_response_contains_city_name(context, city_name):
    """Check that the GraphQL response contains a specific city name."""
    assert context.graphql_data is not None, \
        f"GraphQL data is None. Response: {context.response_data}"
    assert 'city' in context.graphql_data, \
        f"'city' not found in GraphQL data: {context.graphql_data}"
    assert context.graphql_data['city'] is not None, \
        f"'city' is None in GraphQL response"
    assert context.graphql_data['city'].get('name') == city_name, \
        f"Expected city name '{city_name}', got '{context.graphql_data['city'].get('name')}'"


@then('the GraphQL response contains temperature data')
def step_graphql_response_contains_temperature(context):
    """Check that the GraphQL response contains temperature data."""
    assert context.graphql_data is not None, \
        f"GraphQL data is None. Response: {context.response_data}"
    assert 'currentWeather' in context.graphql_data, \
        f"'currentWeather' not found in GraphQL data: {context.graphql_data}"
    weather = context.graphql_data['currentWeather']
    assert weather is not None, "currentWeather is None"
    assert 'temperature' in weather, \
        f"'temperature' not found in currentWeather: {weather}"


@then('the GraphQL response contains humidity data')
def step_graphql_response_contains_humidity(context):
    """Check that the GraphQL response contains humidity data."""
    assert context.graphql_data is not None, \
        f"GraphQL data is None. Response: {context.response_data}"
    assert 'currentWeather' in context.graphql_data, \
        f"'currentWeather' not found in GraphQL data: {context.graphql_data}"
    weather = context.graphql_data['currentWeather']
    assert weather is not None, "currentWeather is None"
    assert 'humidity' in weather, \
        f"'humidity' not found in currentWeather: {weather}"


@then('the GraphQL response contains wind speed data')
def step_graphql_response_contains_wind_speed(context):
    """Check that the GraphQL response contains wind speed data."""
    assert context.graphql_data is not None, \
        f"GraphQL data is None. Response: {context.response_data}"
    assert 'currentWeather' in context.graphql_data, \
        f"'currentWeather' not found in GraphQL data: {context.graphql_data}"
    weather = context.graphql_data['currentWeather']
    assert weather is not None, "currentWeather is None"
    assert 'windSpeed' in weather, \
        f"'windSpeed' not found in currentWeather: {weather}"


@then('the GraphQL response contains forecast data')
def step_graphql_response_contains_forecast(context):
    """Check that the GraphQL response contains forecast data."""
    assert context.graphql_data is not None, \
        f"GraphQL data is None. Response: {context.response_data}"
    assert 'forecast' in context.graphql_data, \
        f"'forecast' not found in GraphQL data: {context.graphql_data}"
    assert isinstance(context.graphql_data['forecast'], list), \
        f"'forecast' should be a list, got {type(context.graphql_data['forecast'])}"


@then('the GraphQL response contains historical weather data')
def step_graphql_response_contains_historical(context):
    """Check that the GraphQL response contains historical weather data."""
    assert context.graphql_data is not None, \
        f"GraphQL data is None. Response: {context.response_data}"
    assert 'historicalWeather' in context.graphql_data, \
        f"'historicalWeather' not found in GraphQL data: {context.graphql_data}"
    historical = context.graphql_data['historicalWeather']
    assert historical is not None, "historicalWeather is None"
    assert 'date' in historical, \
        f"'date' not found in historicalWeather: {historical}"


@then('the GraphQL response contains schema information')
def step_graphql_response_contains_schema(context):
    """Check that the GraphQL response contains schema information."""
    assert context.graphql_data is not None, \
        f"GraphQL data is None. Response: {context.response_data}"
    assert '__schema' in context.graphql_data, \
        f"'__schema' not found in GraphQL data: {context.graphql_data}"
    schema = context.graphql_data['__schema']
    assert 'types' in schema, \
        f"'types' not found in schema: {schema}"
    assert 'queryType' in schema, \
        f"'queryType' not found in schema: {schema}"
