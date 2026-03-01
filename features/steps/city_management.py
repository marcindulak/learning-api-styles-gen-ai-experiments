"""Step definitions for city management features."""

import json
import subprocess

from behave import given, then, when

from src.weather.models import City


@given('I am authenticated as admin')
def step_authenticated_as_admin(context):
    """Authenticate as admin user and store access token."""
    payload = json.dumps({"username": "admin", "password": "admin"})
    result = subprocess.run(
        [
            'curl',
            '--data', payload,
            '--header', 'Content-Type: application/json',
            '--request', 'POST',
            '--silent',
            f'http://localhost:8000/api/jwt/obtain'
        ],
        capture_output=True,
        text=True,
        timeout=10
    )
    response = json.loads(result.stdout)
    context.access_token = response['access']


@given('I am authenticated as a regular user')
def step_authenticated_as_regular_user(context):
    """Authenticate as a regular user and store access token."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    if not User.objects.filter(username='user').exists():
        User.objects.create_user('user', 'user@example.com', 'password')

    payload = json.dumps({"username": "user", "password": "password"})
    result = subprocess.run(
        [
            'curl',
            '--data', payload,
            '--header', 'Content-Type: application/json',
            '--request', 'POST',
            '--silent',
            f'http://localhost:8000/api/jwt/obtain'
        ],
        capture_output=True,
        text=True,
        timeout=10
    )
    response = json.loads(result.stdout)
    context.access_token = response['access']


@given('a city "{city_name}" exists')
def step_city_exists(context, city_name: str):
    """Create a city in the database."""
    if not City.objects.filter(name=city_name).exists():
        City.objects.create(
            name=city_name,
            country='Denmark',
            region='Europe',
            timezone='Europe/Copenhagen',
            latitude=55.676100,
            longitude=12.568300
        )


@given('a city "{city_name}" with UUID exists')
def step_city_with_uuid_exists(context, city_name: str):
    """Create a city and store its UUID."""
    city, _ = City.objects.get_or_create(
        name=city_name,
        defaults={
            'country': 'Denmark',
            'region': 'Europe',
            'timezone': 'Europe/Copenhagen',
            'latitude': 55.676100,
            'longitude': 12.568300
        }
    )
    context.city_uuid = str(city.uuid)


@when('I send a POST request to "{endpoint}" with city data:')
def step_post_city_data(context, endpoint: str):
    """Send a POST request with city data from the table."""
    data = {}
    # Behave treats the first row as headers
    # Since our table is key-value pairs, we need to include the headers as the first data row
    headers = context.table.headings
    if len(headers) == 2:
        # First row became headers, so add it as data
        data[headers[0].strip()] = headers[1].strip()

    # Then process the remaining rows
    for row in context.table:
        field_name = row.cells[0].strip()
        field_value = row.cells[1].strip()
        data[field_name] = field_value

    # Convert numeric fields
    if 'latitude' in data:
        data['latitude'] = float(data['latitude'])
    if 'longitude' in data:
        data['longitude'] = float(data['longitude'])

    payload = json.dumps(data)

    headers = ['Content-Type: application/json']
    if hasattr(context, 'access_token'):
        headers.append(f'Authorization: Bearer {context.access_token}')

    # Add trailing slash if not present
    if not endpoint.endswith('/'):
        endpoint += '/'

    cmd = [
        'curl',
        '--data', payload,
        '--request', 'POST',
        '--silent',
        '--write-out', '\\n%{http_code}',
        f'http://localhost:8000{endpoint}'
    ]

    for header in headers:
        cmd.extend(['--header', header])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=10
    )

    lines = result.stdout.strip().split('\n')
    context.response_status_code = int(lines[-1])
    context.response_body = '\n'.join(lines[:-1]) if len(lines) > 1 else ''

    try:
        context.response_json = json.loads(context.response_body) if context.response_body else {}
    except json.JSONDecodeError:
        context.response_json = {}


@when('I send a GET request to "{endpoint}"')
def step_get_request(context, endpoint: str):
    """Send a GET request to the specified endpoint."""
    # Replace {uuid} placeholder if present
    if '{uuid}' in endpoint and hasattr(context, 'city_uuid'):
        endpoint = endpoint.replace('{uuid}', context.city_uuid)

    # Add trailing slash before query parameters or at end
    if '?' in endpoint:
        # Has query parameters - add slash before the ?
        if '/?' not in endpoint:
            endpoint = endpoint.replace('?', '/?', 1)
    elif not endpoint.endswith('/'):
        # No query parameters - add slash at end
        endpoint += '/'

    cmd = [
        'curl',
        '--request', 'GET',
        '--silent',
        '--write-out', '\\n%{http_code}',
        f'http://localhost:8000{endpoint}'
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=10
    )

    lines = result.stdout.strip().split('\n')
    context.response_status_code = int(lines[-1])
    context.response_body = '\n'.join(lines[:-1]) if len(lines) > 1 else ''

    try:
        context.response_json = json.loads(context.response_body) if context.response_body else {}
    except json.JSONDecodeError:
        context.response_json = {}


@then('the response contains a "{field}" field')
def step_response_contains_field(context, field: str):
    """Verify the response contains the specified field."""
    assert field in context.response_json, \
        f"Expected field '{field}' in response, got: {context.response_json}"


@then('the response contains field "{field}" with value "{value}"')
def step_response_field_value(context, field: str, value: str):
    """Verify the response contains a field with the expected value."""
    assert field in context.response_json, \
        f"Expected field '{field}' in response, got: {context.response_json}"
    actual_value = str(context.response_json[field])
    assert actual_value == value, \
        f"Expected field '{field}' to be '{value}', got '{actual_value}'"


@then('the response contains a list with city "{city_name}"')
def step_response_list_contains_city(context, city_name: str):
    """Verify the response contains a list with the specified city."""
    assert 'results' in context.response_json, \
        f"Expected 'results' field in response, got: {context.response_json}"
    results = context.response_json['results']
    assert isinstance(results, list), \
        f"Expected 'results' to be a list, got: {type(results)}"
    city_names = [city.get('name') for city in results]
    assert city_name in city_names, \
        f"Expected city '{city_name}' in results, got: {city_names}"


@then('the response contains field "{field}" with {count:d} items')
def step_response_field_item_count(context, field: str, count: int):
    """Verify the response field contains the expected number of items."""
    assert field in context.response_json, \
        f"Expected field '{field}' in response, got: {context.response_json}"
    items = context.response_json[field]
    assert isinstance(items, list), \
        f"Expected field '{field}' to be a list, got: {type(items)}"
    assert len(items) == count, \
        f"Expected {count} items in '{field}', got {len(items)}"


@then('the first result has field "{field}" with value "{value}"')
def step_first_result_field_value(context, field: str, value: str):
    """Verify the first result contains a field with the expected value."""
    assert 'results' in context.response_json, \
        f"Expected 'results' field in response, got: {context.response_json}"
    results = context.response_json['results']
    assert len(results) > 0, "Expected at least one result"
    first_result = results[0]
    assert field in first_result, \
        f"Expected field '{field}' in first result, got: {first_result}"
    actual_value = str(first_result[field])
    assert actual_value == value, \
        f"Expected field '{field}' to be '{value}', got '{actual_value}'"
