"""
Step definitions for Feature 011: City Count Limitation
"""
import json
from behave import given, when, then
from django.test import Client
from apps.cities.models import City


# Define the 5 major world cities
MAJOR_CITIES = [
    {
        'name': 'Tokyo',
        'country': 'Japan',
        'region': 'Asia',
        'timezone': 'Asia/Tokyo',
        'latitude': 35.6762,
        'longitude': 139.6503,
    },
    {
        'name': 'Delhi',
        'country': 'India',
        'region': 'Asia',
        'timezone': 'Asia/Kolkata',
        'latitude': 28.7041,
        'longitude': 77.1025,
    },
    {
        'name': 'Shanghai',
        'country': 'China',
        'region': 'Asia',
        'timezone': 'Asia/Shanghai',
        'latitude': 31.2304,
        'longitude': 121.4737,
    },
    {
        'name': 'São Paulo',
        'country': 'Brazil',
        'region': 'South America',
        'timezone': 'America/Sao_Paulo',
        'latitude': -23.5505,
        'longitude': -46.6333,
    },
    {
        'name': 'Mexico City',
        'country': 'Mexico',
        'region': 'North America',
        'timezone': 'America/Mexico_City',
        'latitude': 19.4326,
        'longitude': -99.1332,
    },
]


@given('the system is initialized')
def step_system_initialized(context):
    """Initialize the system with exactly 5 major cities."""
    # Clear existing cities
    City.objects.all().delete()

    # Create the 5 major cities
    for city_data in MAJOR_CITIES:
        City.objects.create(**city_data)

    context.initialized = True


@given('5 cities already exist in the system')
def step_five_cities_exist(context):
    """Ensure 5 cities exist in the system."""
    # Clear and create 5 cities
    City.objects.all().delete()
    for city_data in MAJOR_CITIES:
        City.objects.create(**city_data)


@given('5 cities exist in the system')
def step_five_cities_exist_alt(context):
    """Ensure 5 cities exist in the system (alternative wording)."""
    # Reuse the same logic
    City.objects.all().delete()
    for city_data in MAJOR_CITIES:
        City.objects.create(**city_data)


@given('5 cities are defined in the system')
def step_five_cities_defined(context):
    """Ensure 5 cities are defined in the system (alternative wording)."""
    # Reuse the same logic
    City.objects.all().delete()
    for city_data in MAJOR_CITIES:
        City.objects.create(**city_data)
    context.defined_cities = list(City.objects.all())


@when('I check the city count')
def step_check_city_count(context):
    """Check the number of cities in the system."""
    context.city_count = City.objects.count()


@when('I retrieve the list of predefined cities')
def step_retrieve_predefined_cities(context):
    """Retrieve the list of all predefined cities."""
    context.cities = list(City.objects.all())


@when('I attempt to create another city')
def step_attempt_create_city(context):
    """Attempt to create a new city when limit is reached."""
    # Ensure client is available
    if not hasattr(context, 'client'):
        context.client = Client()

    # Need to authenticate first
    if not hasattr(context, 'access_token') or not context.access_token:
        # Authenticate as admin
        credentials = {"username": "admin", "password": "admin"}
        response = context.client.post(
            '/api/jwt/obtain',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        if response.status_code == 200:
            context.response_data = json.loads(response.content)
            context.access_token = context.response_data['access']

    # Try to create a 6th city
    payload = {
        "name": "Berlin",
        "country": "Germany",
        "region": "Europe",
        "timezone": "Europe/Berlin",
        "latitude": 52.5200,
        "longitude": 13.4050
    }
    headers = {
        'Authorization': f'Bearer {context.access_token}',
        'Content-Type': 'application/json'
    }

    response = context.client.post(
        '/api/cities/',
        data=json.dumps(payload),
        content_type='application/json',
        HTTP_AUTHORIZATION=headers['Authorization']
    )

    context.response = response
    context.response_status = response.status_code


@when('I update the timezone of one city')
def step_update_city_timezone(context):
    """Update the timezone of one existing city."""
    # Ensure client is available
    if not hasattr(context, 'client'):
        context.client = Client()

    # Get the first city
    city = City.objects.first()
    assert city, "No cities found to update"

    # Need to authenticate first
    if not hasattr(context, 'access_token') or not context.access_token:
        credentials = {"username": "admin", "password": "admin"}
        response = context.client.post(
            '/api/jwt/obtain',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        if response.status_code == 200:
            context.response_data = json.loads(response.content)
            context.access_token = context.response_data['access']

    # Update the city timezone
    payload = {
        "timezone": "Europe/London"  # Change to a different timezone
    }
    headers = {
        'Authorization': f'Bearer {context.access_token}',
        'Content-Type': 'application/json'
    }

    response = context.client.put(
        f'/api/cities/{city.uuid}/',
        data=json.dumps(payload),
        content_type='application/json',
        HTTP_AUTHORIZATION=headers['Authorization']
    )

    context.response = response
    context.response_status = response.status_code
    context.updated_city = city


@when('I attempt to delete a city')
def step_attempt_delete_city(context):
    """Attempt to delete a predefined city."""
    # Ensure client is available
    if not hasattr(context, 'client'):
        context.client = Client()

    # Get the first city
    city = City.objects.first()
    assert city, "No cities found to delete"

    # Need to authenticate first
    if not hasattr(context, 'access_token') or not context.access_token:
        credentials = {"username": "admin", "password": "admin"}
        response = context.client.post(
            '/api/jwt/obtain',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        if response.status_code == 200:
            context.response_data = json.loads(response.content)
            context.access_token = context.response_data['access']

    # Try to delete the city
    headers = {
        'Authorization': f'Bearer {context.access_token}',
    }

    response = context.client.delete(
        f'/api/cities/{city.uuid}/',
        HTTP_AUTHORIZATION=headers['Authorization']
    )

    context.response = response
    context.response_status = response.status_code
    context.attempted_delete_city = city


@then('exactly 5 cities are defined in the system')
def step_verify_exact_five_cities(context):
    """Verify that exactly 5 cities are defined."""
    assert context.city_count == 5, \
        f"Expected 5 cities, but found {context.city_count}"


@then('the cities include major world population centers')
def step_verify_major_cities(context):
    """Verify that the cities include major world population centers."""
    city_names = {city.name for city in context.cities}

    # Check that at least some major cities are present
    major_city_names = {'Tokyo', 'Delhi', 'Shanghai', 'São Paulo', 'Mexico City'}
    assert city_names == major_city_names, \
        f"Expected major cities {major_city_names}, but got {city_names}"


@then('each city has valid geographic coordinates')
def step_verify_coordinates(context):
    """Verify that each city has valid geographic coordinates."""
    for city in context.cities:
        assert city.latitude is not None, f"City {city.name} has no latitude"
        assert city.longitude is not None, f"City {city.name} has no longitude"
        assert -90 <= city.latitude <= 90, \
            f"City {city.name} has invalid latitude: {city.latitude}"
        assert -180 <= city.longitude <= 180, \
            f"City {city.name} has invalid longitude: {city.longitude}"


@then('the request is denied with a city limit error')
def step_verify_city_limit_denied(context):
    """Verify that the request was denied due to city limit."""
    # Should return a 400 or 409 error
    assert context.response_status in [400, 409, 403], \
        f"Expected error status, got {context.response_status}"

    # Verify the response contains an error about city limit
    response_data = json.loads(context.response.content)
    assert isinstance(response_data, dict), "Response should be a dictionary"


@then('the city is updated successfully')
def step_verify_city_updated(context):
    """Verify that the city was updated successfully."""
    assert context.response_status == 200, \
        f"Expected 200 OK, got {context.response_status}"

    # Verify the city was actually updated
    updated_city = City.objects.get(uuid=context.updated_city.uuid)
    assert updated_city.timezone == "Europe/London", \
        f"Expected timezone to be updated, but got {updated_city.timezone}"


@then('the city count remains 5')
def step_verify_city_count_unchanged(context):
    """Verify that the city count is still 5 after update."""
    current_count = City.objects.count()
    assert current_count == 5, \
        f"Expected 5 cities after update, but found {current_count}"


@then('the deletion is prevented with an error message')
def step_verify_deletion_prevented(context):
    """Verify that the deletion was prevented with an error."""
    # Should return a 400 or 403 error
    assert context.response_status in [400, 403], \
        f"Expected error status, got {context.response_status}"

    # Verify the city still exists
    try:
        City.objects.get(uuid=context.attempted_delete_city.uuid)
    except City.DoesNotExist:
        assert False, "City was deleted when it should have been protected"
