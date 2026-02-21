"""
Step definitions for city management features.
"""
from behave import given, when, then
from django.contrib.auth import get_user_model
from django.test import Client
from weather.models import City
import json

User = get_user_model()


@given('I am an admin user')
def step_admin_user(context):
    """Create and authenticate an admin user."""
    context.user = User.objects.create_user(username='admin', password='admin', is_staff=True)
    context.client = Client()
    context.client.force_login(context.user)


@given('I am a regular user')
def step_regular_user(context):
    """Create and authenticate a regular user."""
    context.user = User.objects.create_user(username='user', password='user')
    context.client = Client()
    context.client.force_login(context.user)


@given('a city "{name}" exists in "{country}"')
def step_city_exists(context, name, country):
    """Create a city with given name and country."""
    context.city = City.objects.create(
        name=name,
        country=country,
        region='Test Region',
        timezone='UTC',
        latitude=0.0,
        longitude=0.0
    )


@given('cities exist')
def step_cities_exist(context):
    """Create multiple cities from table."""
    context.cities = []
    for row in context.table:
        city = City.objects.create(
            name=row['name'],
            country=row['country'],
            region='Test Region',
            timezone='UTC',
            latitude=0.0,
            longitude=0.0
        )
        context.cities.append(city)


@when('I create a city with name "{name}" in "{country}"')
def step_create_city(context, name, country):
    """Create a city via API."""
    data = {
        'name': name,
        'country': country,
        'region': 'Test Region',
        'timezone': 'UTC',
        'latitude': 0.0,
        'longitude': 0.0
    }
    context.response = context.client.post(
        '/api/cities/',
        data=json.dumps(data),
        content_type='application/json'
    )


@when('I list all cities')
def step_list_cities(context):
    """List all cities via API."""
    context.response = context.client.get('/api/cities/')


@when('I try to create a city with name "{name}" in "{country}"')
def step_try_create_city(context, name, country):
    """Attempt to create a city (may fail due to permissions)."""
    data = {
        'name': name,
        'country': country,
        'region': 'Test Region',
        'timezone': 'UTC',
        'latitude': 0.0,
        'longitude': 0.0
    }
    context.response = context.client.post(
        '/api/cities/',
        data=json.dumps(data),
        content_type='application/json'
    )


@when('I update the city "{name}" to have timezone "{timezone}"')
def step_update_city(context, name, timezone):
    """Update a city via API."""
    city = City.objects.get(name=name)
    data = {
        'name': city.name,
        'country': city.country,
        'region': city.region,
        'timezone': timezone,
        'latitude': city.latitude,
        'longitude': city.longitude
    }
    context.response = context.client.put(
        f'/api/cities/{city.uuid}/',
        data=json.dumps(data),
        content_type='application/json'
    )


@when('I try to update the city "{name}"')
def step_try_update_city(context, name):
    """Attempt to update a city (may fail due to permissions)."""
    city = City.objects.get(name=name)
    data = {
        'name': city.name,
        'country': city.country,
        'region': city.region,
        'timezone': 'UTC',
        'latitude': city.latitude,
        'longitude': city.longitude
    }
    context.response = context.client.put(
        f'/api/cities/{city.uuid}/',
        data=json.dumps(data),
        content_type='application/json'
    )


@when('I delete the city "{name}"')
def step_delete_city(context, name):
    """Delete a city via API."""
    city = City.objects.get(name=name)
    context.response = context.client.delete(f'/api/cities/{city.uuid}/')


@when('I search for cities with name "{name}"')
def step_search_cities(context, name):
    """Search for cities by name."""
    context.response = context.client.get(f'/api/cities/?search_name={name}')


@then('the city is created successfully')
def step_city_created(context):
    """Verify city was created."""
    assert context.response.status_code == 201


@then('the city has a UUID')
def step_city_has_uuid(context):
    """Verify created city has UUID."""
    data = context.response.json()
    assert 'uuid' in data
    assert data['uuid'] is not None


@then('I see the city "{name}" in the list')
def step_see_city_in_list(context, name):
    """Verify city appears in list."""
    data = context.response.json()
    cities = data.get('results', [])
    city_names = [c['name'] for c in cities]
    assert name in city_names


@then('I get a 403 Forbidden error')
def step_forbidden_error(context):
    """Verify 403 response."""
    assert context.response.status_code == 403


@then('the city is updated successfully')
def step_city_updated(context):
    """Verify city was updated."""
    assert context.response.status_code == 200


@then('the city is deleted successfully')
def step_city_deleted(context):
    """Verify city was deleted."""
    assert context.response.status_code == 204


@then('I get {count:d} result')
def step_get_count_results(context, count):
    """Verify result count."""
    data = context.response.json()
    results = data.get('results', [])
    assert len(results) == count


@then('the result contains "{name}"')
def step_result_contains(context, name):
    """Verify result contains name."""
    data = context.response.json()
    results = data.get('results', [])
    city_names = [c['name'] for c in results]
    assert name in city_names
