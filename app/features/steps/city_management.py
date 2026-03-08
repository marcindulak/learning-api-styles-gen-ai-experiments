"""
Step definitions for city management and authentication.
"""
import json
import subprocess
import uuid
from behave import given, when
from weather.models import City


@given('I am authenticated as admin')
def step_authenticate_as_admin(context):
    """Authenticate as admin user and store access token."""
    credentials_payload = json.dumps({"username": "admin", "password": "admin"})

    result = subprocess.run(
        [
            "curl",
            "--data", credentials_payload,
            "--header", "Content-Type: application/json",
            "--request", "POST",
            "--silent",
            "http://localhost:8000/api/jwt/obtain"
        ],
        capture_output=True,
        text=True
    )

    response_data = json.loads(result.stdout)
    context.access_token = response_data.get('access')
    context.response_body = result.stdout

    # Get status code
    result_with_code = subprocess.run(
        [
            "curl",
            "--data", credentials_payload,
            "--header", "Content-Type: application/json",
            "--request", "POST",
            "--silent",
            "--output", "/dev/null",
            "--write-out", "%{http_code}",
            "http://localhost:8000/api/jwt/obtain"
        ],
        capture_output=True,
        text=True
    )
    context.response_status_code = int(result_with_code.stdout)


@given('I am authenticated as regular user')
def step_authenticate_as_regular_user(context):
    """Authenticate as regular user and store access token."""
    # Create the user with the same credentials as Feature 001
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if not User.objects.filter(username="user").exists():
        User.objects.create_user(username="user", password="userpass")

    credentials_payload = json.dumps({"username": "user", "password": "userpass"})

    result = subprocess.run(
        [
            "curl",
            "--data", credentials_payload,
            "--header", "Content-Type: application/json",
            "--request", "POST",
            "--silent",
            "http://localhost:8000/api/jwt/obtain"
        ],
        capture_output=True,
        text=True
    )

    response_data = json.loads(result.stdout)
    context.access_token = response_data.get('access')
    context.response_body = result.stdout

    # Get status code
    result_with_code = subprocess.run(
        [
            "curl",
            "--data", credentials_payload,
            "--header", "Content-Type: application/json",
            "--request", "POST",
            "--silent",
            "--output", "/dev/null",
            "--write-out", "%{http_code}",
            "http://localhost:8000/api/jwt/obtain"
        ],
        capture_output=True,
        text=True
    )
    context.response_status_code = int(result_with_code.stdout)


@when('I create a city with the following data:')
def step_create_city(context):
    """Create a city using the REST API."""
    city_data = {}
    # Behave treats first row as headers, so we need to include it as data
    # Add headings first (which is the first row)
    if context.table.headings:
        key = context.table.headings[0]
        value = context.table.headings[1]
        if key in ['latitude', 'longitude']:
            city_data[key] = float(value)
        else:
            city_data[key] = value

    # Then add remaining rows
    for row in context.table:
        key = row.cells[0]
        value = row.cells[1]
        # Convert numeric values
        if key in ['latitude', 'longitude']:
            city_data[key] = float(value)
        else:
            city_data[key] = value

    payload = json.dumps(city_data)

    curl_command = [
        "curl",
        "-s",
        "--data", payload,
        "--header", "Content-Type: application/json",
        "--request", "POST",
        "--write-out", "\n%{http_code}",
    ]

    if hasattr(context, 'access_token') and context.access_token:
        curl_command.append("--header")
        curl_command.append(f"Authorization: Bearer {context.access_token}")

    curl_command.append("http://localhost:8000/api/cities/")

    result = subprocess.run(
        curl_command,
        capture_output=True,
        text=True
    )

    output_lines = result.stdout.strip().split('\n')
    context.response_status_code = int(output_lines[-1])
    context.response_body = '\n'.join(output_lines[:-1]) if len(output_lines) > 1 else ''


@when('I send a GET request to "{endpoint}"')
def step_send_get_request(context, endpoint):
    """Send a GET request to the specified endpoint."""
    # Store the original endpoint for later use
    context.last_endpoint = endpoint

    # Replace {uuid} placeholder if present
    if '{uuid}' in endpoint and hasattr(context, 'stored_uuid'):
        endpoint = endpoint.replace('{uuid}', str(context.stored_uuid))

    # Get status code
    curl_command_code = [
        "curl",
        "--request", "GET",
        "--silent",
        "--output", "/dev/null",
        "--write-out", "%{http_code}",
    ]

    # Add authorization header if access token is available
    if hasattr(context, 'access_token') and context.access_token:
        curl_command_code.append("--header")
        curl_command_code.append(f"Authorization: Bearer {context.access_token}")

    curl_command_code.append(f"http://localhost:8000{endpoint}")

    result_code = subprocess.run(
        curl_command_code,
        capture_output=True,
        text=True
    )
    context.response_status_code = int(result_code.stdout)

    # Get response body
    curl_command_body = [
        "curl",
        "--request", "GET",
        "--silent",
    ]

    # Add authorization header if access token is available
    if hasattr(context, 'access_token') and context.access_token:
        curl_command_body.append("--header")
        curl_command_body.append(f"Authorization: Bearer {context.access_token}")

    curl_command_body.append(f"http://localhost:8000{endpoint}")

    result_body = subprocess.run(
        curl_command_body,
        capture_output=True,
        text=True
    )
    context.response_body = result_body.stdout


@given('a city exists with name "{city_name}"')
def step_city_exists(context, city_name):
    """Create a city in the database."""
    City.objects.create(
        name=city_name,
        country="Test Country",
        region="Test Region",
        timezone="UTC",
        latitude=0.0,
        longitude=0.0
    )


@given('a city exists with name "{city_name}" and UUID is stored')
def step_city_exists_with_uuid_stored(context, city_name):
    """Create a city and store its UUID."""
    city = City.objects.create(
        name=city_name,
        country="Test Country",
        region="Test Region",
        timezone="UTC",
        latitude=0.0,
        longitude=0.0
    )
    context.stored_uuid = city.uuid


# Import the then decorator
from behave import then


@then('the response contains "{text}"')
def step_response_contains(context, text):
    """Verify that the response body contains the specified text."""
    assert text in context.response_body, \
        f"Text '{text}' not found in response: {context.response_body}"


@then('the response has field "{field_name}" equals "{expected_value}"')
def step_response_field_equals(context, field_name, expected_value):
    """Verify that the response field equals the expected value."""
    import json
    response_data = json.loads(context.response_body)
    actual_value = response_data.get(field_name)
    assert str(actual_value) == expected_value, \
        f"Field '{field_name}' has value '{actual_value}', expected '{expected_value}'"
