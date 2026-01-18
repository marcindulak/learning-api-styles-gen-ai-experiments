import json
from behave import given, when, then
from django.contrib.auth.models import User
from apps.cities.models import City


@given("I am authenticated as an admin user")
def step_auth_as_admin(context):
    """Authenticate as admin user and obtain JWT token."""
    credentials = {"username": "admin", "password": "admin"}
    response = context.client.post(
        '/api/jwt/obtain',
        data=json.dumps(credentials),
        content_type='application/json'
    )
    assert response.status_code == 200
    context.response_data = json.loads(response.content)
    context.access_token = context.response_data['access']
    context.response = response


@given("I am authenticated as a regular user")
def step_auth_as_regular_user(context):
    """Authenticate as regular user and obtain JWT token."""
    credentials = {"username": "user", "password": "password"}
    response = context.client.post(
        '/api/jwt/obtain',
        data=json.dumps(credentials),
        content_type='application/json'
    )
    assert response.status_code == 200
    context.response_data = json.loads(response.content)
    context.access_token = context.response_data['access']
    context.response = response


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
