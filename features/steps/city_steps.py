"""
Step definitions for Feature 002: City Management
"""
from behave import given, when, then
from django.contrib.auth.models import User
import json


# City data lookup for reuse across scenarios
CITY_DATA = {
    'Tokyo': {
        'name': 'Tokyo',
        'country': 'Japan',
        'region': 'Asia',
        'timezone': 'Asia/Tokyo',
        'latitude': 35.689500,
        'longitude': 139.691700,
    },
    'Delhi': {
        'name': 'Delhi',
        'country': 'India',
        'region': 'Asia',
        'timezone': 'Asia/Kolkata',
        'latitude': 28.679100,
        'longitude': 77.069700,
    },
    'Shanghai': {
        'name': 'Shanghai',
        'country': 'China',
        'region': 'Asia',
        'timezone': 'Asia/Shanghai',
        'latitude': 31.224400,
        'longitude': 121.469200,
    },
    'SaoPaulo': {
        'name': 'SaoPaulo',
        'country': 'Brazil',
        'region': 'South America',
        'timezone': 'America/Sao_Paulo',
        'latitude': -23.550520,
        'longitude': -46.633308,
    },
    'MexicoCity': {
        'name': 'MexicoCity',
        'country': 'Mexico',
        'region': 'North America',
        'timezone': 'America/Mexico_City',
        'latitude': 19.432608,
        'longitude': -99.133209,
    },
    'Mumbai': {
        'name': 'Mumbai',
        'country': 'India',
        'region': 'Asia',
        'timezone': 'Asia/Kolkata',
        'latitude': 19.076090,
        'longitude': 72.877426,
    },
    'TestCity': {
        'name': 'TestCity',
        'country': 'TestCountry',
        'region': 'TestRegion',
        'timezone': 'UTC',
        'latitude': 0.0,
        'longitude': 0.0,
    },
}


def create_city_via_api(context, city_data):
    """Helper function to create a city via the API."""
    # Get admin token if not already present
    if not hasattr(context, 'access_token') or context.access_token is None:
        # Need to get admin token first
        from features.steps.authentication_steps import request_jwt_token
        request_jwt_token(context, 'admin', 'admin')

    response = context.client.post(
        '/api/cities',
        data=json.dumps(city_data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {context.access_token}',
    )
    return response


def get_city_uuid_by_name(context, city_name):
    """Helper function to get city UUID by name via search."""
    response = context.client.get(
        f'/api/cities?search={city_name}',
        HTTP_AUTHORIZATION=f'Bearer {context.access_token}',
    )
    if response.status_code == 200:
        data = json.loads(response.content)
        results = data.get('results', [])
        for city in results:
            if city.get('name') == city_name:
                return city.get('uuid')
    return None


@when('I create a city with the following details:')
def step_create_city_with_details(context):
    """Create a city with details from a data table."""
    row = context.table[0]
    city_data = {
        'name': row['name'],
        'country': row['country'],
        'region': row['region'],
        'timezone': row['timezone'],
        'latitude': float(row['latitude']),
        'longitude': float(row['longitude']),
    }

    context.response = context.client.post(
        '/api/cities',
        data=json.dumps(city_data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {context.access_token}',
    )

    try:
        context.response_data = json.loads(context.response.content)
    except (json.JSONDecodeError, ValueError):
        context.response_data = None


@then('the response contains the city name "{city_name}"')
def step_response_contains_city_name(context, city_name):
    """Check that the response contains the specified city name.

    Handles both single city responses and paginated list responses.
    """
    assert context.response_data is not None, "Response data is None"

    # Check if this is a paginated list response
    if 'results' in context.response_data:
        # Search in results
        found = False
        for city in context.response_data['results']:
            if city.get('name') == city_name:
                found = True
                break
        assert found, f"City '{city_name}' not found in results: {context.response_data}"
    else:
        # Single city response
        assert 'name' in context.response_data, f"'name' field not found in response: {context.response_data}"
        assert context.response_data['name'] == city_name, \
            f"Expected city name '{city_name}', got '{context.response_data.get('name')}'"


@then('the response contains a "{field}" field')
def step_response_contains_field(context, field):
    """Check that the response contains a specific field."""
    assert context.response_data is not None, "Response data is None"
    assert field in context.response_data, f"'{field}' field not found in response: {context.response_data}"


@given('a city "{city_name}" exists in the system')
def step_city_exists(context, city_name):
    """Ensure a city exists in the system by creating it via the API."""
    # Get city data from lookup or create default
    if city_name in CITY_DATA:
        city_data = CITY_DATA[city_name].copy()
    else:
        city_data = {
            'name': city_name,
            'country': 'TestCountry',
            'region': 'TestRegion',
            'timezone': 'UTC',
            'latitude': 0.0,
            'longitude': 0.0,
        }

    if not hasattr(context, 'city_uuids'):
        context.city_uuids = {}

    # Check if city already exists via API search
    search_response = context.client.get(
        f'/api/cities?search={city_name}',
        HTTP_AUTHORIZATION=f'Bearer {context.access_token}',
    )
    if search_response.status_code == 200:
        search_data = json.loads(search_response.content)
        for city in search_data.get('results', []):
            if city.get('name') == city_name:
                context.city_uuids[city_name] = city.get('uuid')
                return

    # Create city via API
    response = context.client.post(
        '/api/cities',
        data=json.dumps(city_data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {context.access_token}',
    )

    if response.status_code == 201:
        data = json.loads(response.content)
        context.city_uuids[city_name] = data.get('uuid')
    else:
        # If creation fails (e.g., limit reached), try to get existing one
        # This can happen if a previous scenario created it
        search_response = context.client.get(
            f'/api/cities?search={city_name}',
            HTTP_AUTHORIZATION=f'Bearer {context.access_token}',
        )
        if search_response.status_code == 200:
            search_data = json.loads(search_response.content)
            for city in search_data.get('results', []):
                if city.get('name') == city_name:
                    context.city_uuids[city_name] = city.get('uuid')
                    return
        raise AssertionError(f"Failed to create city '{city_name}': {response.content}")


@when('I retrieve the city "{city_name}" by its UUID')
def step_retrieve_city_by_uuid(context, city_name):
    """Retrieve a city by its UUID."""
    assert hasattr(context, 'city_uuids') and city_name in context.city_uuids, \
        f"City UUID for '{city_name}' not found"

    city_uuid = context.city_uuids[city_name]

    context.response = context.client.get(
        f'/api/cities/{city_uuid}',
        HTTP_AUTHORIZATION=f'Bearer {context.access_token}',
    )

    try:
        context.response_data = json.loads(context.response.content)
    except (json.JSONDecodeError, ValueError):
        context.response_data = None


@given('the following cities exist in the system:')
def step_cities_exist_in_system(context):
    """Create multiple cities from a data table via API."""
    if not hasattr(context, 'city_uuids'):
        context.city_uuids = {}

    for row in context.table:
        city_name = row['name']

        # Check if city already exists via API search
        search_response = context.client.get(
            f'/api/cities?search={city_name}',
            HTTP_AUTHORIZATION=f'Bearer {context.access_token}',
        )
        if search_response.status_code == 200:
            search_data = json.loads(search_response.content)
            for city in search_data.get('results', []):
                if city.get('name') == city_name:
                    context.city_uuids[city_name] = city.get('uuid')
                    break
            else:
                # City not found, need to create
                city_data = {
                    'name': city_name,
                    'country': row['country'],
                    'region': row['region'],
                    'timezone': row['timezone'],
                    'latitude': float(row['latitude']),
                    'longitude': float(row['longitude']),
                }

                # Create city via API
                response = context.client.post(
                    '/api/cities',
                    data=json.dumps(city_data),
                    content_type='application/json',
                    HTTP_AUTHORIZATION=f'Bearer {context.access_token}',
                )

                if response.status_code == 201:
                    data = json.loads(response.content)
                    context.city_uuids[city_name] = data.get('uuid')
                else:
                    raise AssertionError(f"Failed to create city '{city_name}': {response.content}")


@then('the response contains a list of cities')
def step_response_contains_city_list(context):
    """Check that the response contains a list of cities."""
    assert context.response_data is not None, "Response data is None"
    assert 'results' in context.response_data, f"'results' field not found in response: {context.response_data}"
    assert isinstance(context.response_data['results'], list), \
        f"'results' should be a list, got {type(context.response_data['results'])}"


@when('I search for cities with name "{city_name}"')
def step_search_cities_by_name(context, city_name):
    """Search for cities by name."""
    context.response = context.client.get(
        f'/api/cities?search={city_name}',
        HTTP_AUTHORIZATION=f'Bearer {context.access_token}',
    )

    try:
        context.response_data = json.loads(context.response.content)
    except (json.JSONDecodeError, ValueError):
        context.response_data = None


@when('I update the city "{city_name}" with country "{country}"')
def step_update_city_country(context, city_name, country):
    """Update a city's country field."""
    assert hasattr(context, 'city_uuids') and city_name in context.city_uuids, \
        f"City UUID for '{city_name}' not found"

    city_uuid = context.city_uuids[city_name]

    context.response = context.client.patch(
        f'/api/cities/{city_uuid}',
        data=json.dumps({'country': country}),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {context.access_token}',
    )

    try:
        context.response_data = json.loads(context.response.content)
    except (json.JSONDecodeError, ValueError):
        context.response_data = None


@then('the response contains the country "{country}"')
def step_response_contains_country(context, country):
    """Check that the response contains the specified country."""
    assert context.response_data is not None, "Response data is None"
    assert 'country' in context.response_data, f"'country' field not found in response: {context.response_data}"
    assert context.response_data['country'] == country, \
        f"Expected country '{country}', got '{context.response_data.get('country')}'"


@when('I delete the city "{city_name}"')
def step_delete_city(context, city_name):
    """Delete a city by its name."""
    assert hasattr(context, 'city_uuids') and city_name in context.city_uuids, \
        f"City UUID for '{city_name}' not found"

    city_uuid = context.city_uuids[city_name]

    context.response = context.client.delete(
        f'/api/cities/{city_uuid}',
        HTTP_AUTHORIZATION=f'Bearer {context.access_token}',
    )

    try:
        context.response_data = json.loads(context.response.content)
    except (json.JSONDecodeError, ValueError):
        context.response_data = None


@then('the city "{city_name}" no longer exists')
def step_city_no_longer_exists(context, city_name):
    """Verify that a city no longer exists in the system via API."""
    search_response = context.client.get(
        f'/api/cities?search={city_name}',
        HTTP_AUTHORIZATION=f'Bearer {context.access_token}',
    )
    if search_response.status_code == 200:
        search_data = json.loads(search_response.content)
        for city in search_data.get('results', []):
            if city.get('name') == city_name:
                raise AssertionError(f"City '{city_name}' still exists in the system")


@then('the response contains error message about city limit')
def step_response_contains_city_limit_error(context):
    """Check that the response contains an error about city limit."""
    assert context.response_data is not None, "Response data is None"
    # The error message could be in various formats depending on DRF
    response_str = str(context.response_data).lower()
    assert 'cannot create more than' in response_str or '5' in response_str, \
        f"Expected error about city limit, got: {context.response_data}"
