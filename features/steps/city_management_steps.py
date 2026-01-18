import json
from behave import given, when, then
from django.contrib.auth.models import User
from apps.cities.models import City
from django.test import Client
from rest_framework_simplejwt.tokens import AccessToken


def get_jwt_token_for_user(user):
    """Generate a JWT token for a user."""
    access_token = AccessToken.for_user(user)
    return str(access_token)


@when("I create a city with name \"{name}\", country \"{country}\", region \"{region}\", timezone \"{timezone}\", latitude {latitude}, longitude {longitude}")
def step_create_city(context, name, country, region, timezone, latitude, longitude):
    """Create a city via REST API."""
    payload = {
        "name": name,
        "country": country,
        "region": region,
        "timezone": timezone,
        "latitude": float(latitude),
        "longitude": float(longitude)
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
    if response.status_code == 201:
        context.response_data = json.loads(response.content)
        context.cities[name] = context.response_data


@then("the city is created successfully")
def step_city_created_successfully(context):
    """Verify city was created successfully."""
    assert context.response.status_code == 201, f"Expected 201, got {context.response.status_code}"


@then("the city has a UUID identifier")
def step_city_has_uuid(context):
    """Verify city has UUID identifier."""
    assert 'uuid' in context.response_data
    assert context.response_data['uuid'] is not None


@given("a city \"{city_name}\" exists with UUID")
def step_city_exists_with_uuid(context, city_name):
    """Ensure a city exists and store its UUID."""
    # Check if city already exists
    city = City.objects.filter(name=city_name).first()
    if not city:
        # Create the city
        city = City.objects.create(
            name=city_name,
            country="Test Country",
            region="Test Region",
            timezone="UTC",
            latitude=0.0,
            longitude=0.0
        )
    context.cities[city_name] = {'uuid': str(city.uuid)}


@when("I retrieve the city by UUID")
def step_retrieve_city_by_uuid(context):
    """Retrieve city by UUID via REST API."""
    city_uuid = next(iter(context.cities.values()))['uuid']
    headers = {
        'Authorization': f'Bearer {context.access_token}',
    }
    response = context.client.get(
        f'/api/cities/{city_uuid}/',
        HTTP_AUTHORIZATION=headers['Authorization']
    )
    context.response = response
    if response.status_code == 200:
        context.response_data = json.loads(response.content)


@then("the city details are returned with all fields intact")
def step_city_details_returned(context):
    """Verify city details are returned with all fields."""
    assert context.response.status_code == 200
    assert 'uuid' in context.response_data
    assert 'name' in context.response_data
    assert 'country' in context.response_data
    assert 'region' in context.response_data
    assert 'timezone' in context.response_data
    assert 'latitude' in context.response_data
    assert 'longitude' in context.response_data


@given("cities \"{cities_str}\" exist")
def step_cities_exist(context, cities_str):
    """Ensure multiple cities exist."""
    city_names = [c.strip().strip('\"') for c in cities_str.split(',')]
    for city_name in city_names:
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
        context.cities[city_name] = {'uuid': str(city.uuid)}


@when("I request a list of all cities")
def step_list_all_cities(context):
    """List all cities via REST API."""
    headers = {
        'Authorization': f'Bearer {context.access_token}',
    }
    response = context.client.get(
        '/api/cities/',
        HTTP_AUTHORIZATION=headers['Authorization']
    )
    context.response = response
    if response.status_code == 200:
        context.response_data = json.loads(response.content)


@then("all {count} cities are returned in the list")
def step_all_cities_returned(context, count):
    """Verify all cities are returned."""
    assert context.response.status_code == 200
    results = context.response_data.get('results', context.response_data)
    assert len(results) == int(count), f"Expected {count} cities, got {len(results)}"


@when("I search for cities with name \"{search_term}\"")
def step_search_cities(context, search_term):
    """Search for cities by name via REST API."""
    headers = {
        'Authorization': f'Bearer {context.access_token}',
    }
    response = context.client.get(
        f'/api/cities/?search={search_term}',
        HTTP_AUTHORIZATION=headers['Authorization']
    )
    context.response = response
    if response.status_code == 200:
        context.response_data = json.loads(response.content)


@then("only \"{expected_city}\" is returned in the results")
def step_only_one_city_returned(context, expected_city):
    """Verify only one city is returned in search results."""
    assert context.response.status_code == 200
    results = context.response_data.get('results', context.response_data)
    assert len(results) == 1, f"Expected 1 city, got {len(results)}"
    assert results[0]['name'] == expected_city


@given("a city \"{city_name}\" exists")
def step_city_exists(context, city_name):
    """Ensure a city exists."""
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
    context.cities[city_name] = {'uuid': str(city.uuid)}


@when("I update the city timezone to \"{new_timezone}\"")
def step_update_city_timezone(context, new_timezone):
    """Update city timezone via REST API."""
    city_uuid = next(iter(context.cities.values()))['uuid']
    payload = {
        "timezone": new_timezone
    }
    headers = {
        'Authorization': f'Bearer {context.access_token}',
        'Content-Type': 'application/json'
    }
    response = context.client.patch(
        f'/api/cities/{city_uuid}/',
        data=json.dumps(payload),
        content_type='application/json',
        HTTP_AUTHORIZATION=headers['Authorization']
    )
    context.response = response
    if response.status_code == 200:
        context.response_data = json.loads(response.content)


@then("the city timezone is updated successfully")
def step_city_timezone_updated(context):
    """Verify city timezone was updated."""
    assert context.response.status_code == 200


@when("I delete the city")
def step_delete_city(context):
    """Delete city via REST API."""
    city_uuid = next(iter(context.cities.values()))['uuid']
    headers = {
        'Authorization': f'Bearer {context.access_token}',
    }
    response = context.client.delete(
        f'/api/cities/{city_uuid}/',
        HTTP_AUTHORIZATION=headers['Authorization']
    )
    context.response = response


@then("the city is removed from the system")
def step_city_removed(context):
    """Verify city was deleted."""
    assert context.response.status_code == 204


@when("I attempt to create a city with name \"{city_name}\"")
def step_attempt_create_city(context, city_name):
    """Attempt to create a city as regular user."""
    payload = {
        "name": city_name,
        "country": "Test Country",
        "region": "Test Region",
        "timezone": "UTC",
        "latitude": 0.0,
        "longitude": 0.0
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
    if response.status_code < 300:
        context.response_data = json.loads(response.content)


@then("the request is denied with a permission error")
def step_request_denied_permission(context):
    """Verify request was denied with permission error."""
    assert context.response.status_code == 403, f"Expected 403, got {context.response.status_code}"


@when("I attempt to delete the city")
def step_attempt_delete_city(context):
    """Attempt to delete city as regular user."""
    city_uuid = next(iter(context.cities.values()))['uuid']
    headers = {
        'Authorization': f'Bearer {context.access_token}',
    }
    response = context.client.delete(
        f'/api/cities/{city_uuid}/',
        HTTP_AUTHORIZATION=headers['Authorization']
    )
    context.response = response


# Feature 002: City Management specific steps

@given('the system has a maximum city limit of 5')
def step_system_has_max_limit(context):
    """Verify the system has a maximum city limit of 5."""
    # This is a configuration verification step - the system is configured to limit cities to 5
    # We just need to ensure 5 cities exist in the system
    City.objects.all().delete()
    major_cities = [
        {'name': 'Tokyo', 'country': 'Japan', 'region': 'Asia', 'timezone': 'Asia/Tokyo', 'latitude': 35.6762, 'longitude': 139.6503},
        {'name': 'Delhi', 'country': 'India', 'region': 'Asia', 'timezone': 'Asia/Kolkata', 'latitude': 28.7041, 'longitude': 77.1025},
        {'name': 'Shanghai', 'country': 'China', 'region': 'Asia', 'timezone': 'Asia/Shanghai', 'latitude': 31.2304, 'longitude': 121.4737},
        {'name': 'São Paulo', 'country': 'Brazil', 'region': 'South America', 'timezone': 'America/Sao_Paulo', 'latitude': -23.5505, 'longitude': -46.6333},
        {'name': 'Mexico City', 'country': 'Mexico', 'region': 'North America', 'timezone': 'America/Mexico_City', 'latitude': 19.4326, 'longitude': -99.1332},
    ]
    for city_data in major_cities:
        City.objects.create(**city_data)
    context.city_limit = 5


@when('an admin user tries to add a 6th city')
def step_admin_tries_add_sixth_city(context):
    """Admin user tries to add a 6th city when limit is reached."""
    # Authenticate as admin by generating a JWT token
    admin_user = User.objects.get(username='admin')
    context.access_token = get_jwt_token_for_user(admin_user)

    # Try to create a 6th city
    new_city_payload = {
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
        data=json.dumps(new_city_payload),
        content_type='application/json',
        HTTP_AUTHORIZATION=headers['Authorization']
    )
    context.response = response
    if response.status_code < 500:
        try:
            context.response_data = json.loads(response.content)
        except:
            context.response_data = {}


@then('the system rejects the new city with an error message')
def step_system_rejects_city(context):
    """Verify the system rejects the 6th city with an error."""
    assert context.response.status_code in [400, 409, 403], f"Expected error status (400/409/403), got {context.response.status_code}"


@then('only the 5 cities remain in the system')
def step_only_five_cities_remain(context):
    """Verify only 5 cities remain in the system."""
    city_count = City.objects.count()
    assert city_count == 5, f"Expected 5 cities, got {city_count}"


@given('an admin user is authenticated')
def step_admin_authenticated(context):
    """Authenticate an admin user and store the access token."""
    # Get the admin user from the database
    admin_user = User.objects.get(username='admin')
    # Generate JWT token for the user
    context.access_token = get_jwt_token_for_user(admin_user)


@when('the admin user creates a city with name "{name}", country "{country}", region "{region}", timezone "{timezone}", latitude {latitude}, longitude {longitude}')
def step_admin_creates_city(context, name, country, region, timezone, latitude, longitude):
    """Admin user creates a city via REST API."""
    payload = {
        "name": name,
        "country": country,
        "region": region,
        "timezone": timezone,
        "latitude": float(latitude),
        "longitude": float(longitude)
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
    if response.status_code == 201:
        context.response_data = json.loads(response.content)
        context.cities[name] = context.response_data


@then('the city is stored in the database')
def step_city_stored_in_database(context):
    """Verify the city is stored in the database."""
    assert context.response.status_code == 201, f"Expected 201, got {context.response.status_code}"
    # Verify city exists in database
    city = City.objects.filter(name=context.response_data['name']).first()
    assert city is not None, f"City {context.response_data['name']} not found in database"


@then('the city has a unique UUID identifier')
def step_city_has_unique_uuid(context):
    """Verify the city has a unique UUID identifier."""
    assert 'uuid' in context.response_data, "UUID not in response"
    assert context.response_data['uuid'] is not None, "UUID is None"


@then('the system returns HTTP 201 Created')
def step_system_returns_201(context):
    """Verify the system returns HTTP 201 Created."""
    assert context.response.status_code == 201, f"Expected 201, got {context.response.status_code}"


@when('the user requests the city by UUID')
def step_user_requests_city_by_uuid(context):
    """User requests a city by UUID."""
    city_uuid = next(iter(context.cities.values()))['uuid']
    headers = {
        'Authorization': f'Bearer {context.access_token}',
    }
    response = context.client.get(
        f'/api/cities/{city_uuid}/',
        HTTP_AUTHORIZATION=headers['Authorization']
    )
    context.response = response
    if response.status_code == 200:
        context.response_data = json.loads(response.content)


@then('the system returns the city data including name, country, region, timezone, latitude, and longitude')
def step_system_returns_complete_city_data(context):
    """Verify the system returns complete city data."""
    assert context.response.status_code == 200, f"Expected 200, got {context.response.status_code}"
    required_fields = ['name', 'country', 'region', 'timezone', 'latitude', 'longitude', 'uuid']
    for field in required_fields:
        assert field in context.response_data, f"Missing field: {field}"
        assert context.response_data[field] is not None, f"Field {field} is None"


@given('a city "{city_name}" exists with UUID "{uuid}"')
def step_city_exists_with_specific_uuid(context, city_name, uuid):
    """Create a city with a specific UUID for testing."""
    # Clear any existing cities
    City.objects.all().delete()

    # Authenticate as admin if not already
    if not hasattr(context, 'access_token') or not context.access_token:
        admin_user = User.objects.get(username='admin')
        context.access_token = get_jwt_token_for_user(admin_user)

    # Create the city with the specified UUID
    city = City.objects.create(
        uuid=uuid,
        name=city_name,
        country="Test Country",
        region="Test Region",
        timezone="UTC",
        latitude=0.0,
        longitude=0.0
    )
    context.cities[city_name] = {'uuid': str(city.uuid)}
