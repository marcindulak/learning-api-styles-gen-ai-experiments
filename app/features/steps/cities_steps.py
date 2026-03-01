"""City management step definitions."""
from behave import given, then, when
from behave.runner import Context


@given('I am authenticated as an admin')
def step_impl(context: Context) -> None:
    """Create admin user and authenticate."""
    from django.contrib.auth.models import User
    from rest_framework.test import APIClient

    context.username = 'admin'
    context.password = 'admin123'
    User.objects.create_superuser(context.username, 'admin@test.com', context.password)

    client = APIClient()
    response = client.post('/api/jwt/obtain', {
        'username': context.username,
        'password': context.password,
    })
    context.access_token = response.json()['access']
    context.client = APIClient()
    context.client.credentials(HTTP_AUTHORIZATION=f'Bearer {context.access_token}')


@when('I create a city with name "{name}" and country "{country}"')
def step_impl(context: Context, name: str, country: str) -> None:
    """Create a city."""
    context.response = context.client.post('/api/cities', {
        'name': name,
        'country': country,
        'region': 'Asia',
        'timezone': 'Asia/Tokyo',
        'latitude': 35.6762,
        'longitude': 139.6503,
    })
    context.city_data = context.response.json() if context.response.status_code == 201 else {}


@then('the city should be created successfully')
def step_impl(context: Context) -> None:
    """Verify city creation."""
    assert context.response.status_code == 201


@then('the city should have a UUID')
def step_impl(context: Context) -> None:
    """Verify city has UUID."""
    assert 'uuid' in context.city_data


@given('there are cities in the database')
def step_impl(context: Context) -> None:
    """Create sample cities."""
    from weather.models import City

    City.objects.create(
        name='Tokyo',
        country='Japan',
        region='Asia',
        timezone='Asia/Tokyo',
        latitude=35.6762,
        longitude=139.6503
    )
    City.objects.create(
        name='New York',
        country='USA',
        region='North America',
        timezone='America/New_York',
        latitude=40.7128,
        longitude=-74.0060
    )


@when('I request the list of cities')
def step_impl(context: Context) -> None:
    """Request list of cities."""
    from rest_framework.test import APIClient

    client = APIClient()
    context.response = client.get('/api/cities')
    context.cities_data = context.response.json() if context.response.status_code == 200 else {}


@then('I should receive a paginated list of cities')
def step_impl(context: Context) -> None:
    """Verify paginated response."""
    assert context.response.status_code == 200
    assert 'results' in context.cities_data
    assert len(context.cities_data['results']) > 0


@given('there is a city named "{name}"')
def step_impl(context: Context, name: str) -> None:
    """Create a city with specific name."""
    from weather.models import City

    City.objects.create(
        name=name,
        country='Denmark',
        region='Europe',
        timezone='Europe/Copenhagen',
        latitude=55.6761,
        longitude=12.5683
    )


@when('I search for cities with name "{name}"')
def step_impl(context: Context, name: str) -> None:
    """Search for cities by name."""
    from rest_framework.test import APIClient

    client = APIClient()
    context.response = client.get(f'/api/cities?search_name={name}')
    context.search_results = context.response.json() if context.response.status_code == 200 else {}


@then('I should find the city "{name}" in the results')
def step_impl(context: Context, name: str) -> None:
    """Verify search results contain the city."""
    assert context.response.status_code == 200
    assert 'results' in context.search_results
    city_names = [city['name'] for city in context.search_results['results']]
    assert name in city_names


@given('there is a city with UUID')
def step_impl(context: Context) -> None:
    """Create a city and store its UUID."""
    from weather.models import City

    city = City.objects.create(
        name='London',
        country='UK',
        region='Europe',
        timezone='Europe/London',
        latitude=51.5074,
        longitude=-0.1278
    )
    context.city_uuid = str(city.uuid)


@when('I request city details by UUID')
def step_impl(context: Context) -> None:
    """Request city details."""
    from rest_framework.test import APIClient

    client = APIClient()
    context.response = client.get(f'/api/cities/{context.city_uuid}')


@then('I should receive the city information')
def step_impl(context: Context) -> None:
    """Verify city information received."""
    assert context.response.status_code == 200
    city_data = context.response.json()
    assert city_data['uuid'] == context.city_uuid


@given('there is a city to update')
def step_impl(context: Context) -> None:
    """Create a city to update."""
    from weather.models import City

    city = City.objects.create(
        name='Paris',
        country='France',
        region='Europe',
        timezone='Europe/Paris',
        latitude=48.8566,
        longitude=2.3522
    )
    context.city_uuid = str(city.uuid)


@when('I update the city timezone')
def step_impl(context: Context) -> None:
    """Update city timezone."""
    context.new_timezone = 'CET'
    context.response = context.client.patch(f'/api/cities/{context.city_uuid}', {
        'timezone': context.new_timezone
    })


@then('the city timezone should be updated')
def step_impl(context: Context) -> None:
    """Verify city timezone updated."""
    from weather.models import City

    assert context.response.status_code == 200
    city = City.objects.get(uuid=context.city_uuid)
    assert city.timezone == context.new_timezone


@given('there is a city to delete')
def step_impl(context: Context) -> None:
    """Create a city to delete."""
    from weather.models import City

    city = City.objects.create(
        name='Berlin',
        country='Germany',
        region='Europe',
        timezone='Europe/Berlin',
        latitude=52.5200,
        longitude=13.4050
    )
    context.city_uuid = str(city.uuid)


@when('I delete the city')
def step_impl(context: Context) -> None:
    """Delete the city."""
    context.response = context.client.delete(f'/api/cities/{context.city_uuid}')


@then('the city should be removed from the database')
def step_impl(context: Context) -> None:
    """Verify city deleted."""
    from weather.models import City

    assert context.response.status_code == 204
    assert not City.objects.filter(uuid=context.city_uuid).exists()
