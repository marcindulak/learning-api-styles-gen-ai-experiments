import uuid

from behave import given, then, when
from django.contrib.auth import get_user_model

from weather_service.models import City

User = get_user_model()


@given("the service is running")
def step_service_is_running(context):
    """Verify the service is running (always true in test environment)."""
    assert True


@given("the following cities exist in the system")
def step_cities_exist_in_system(context):
    """Create cities from table data."""
    for row in context.table:
        City.objects.create(
            name=row["name"],
            country=row["country"],
            region=row["region"],
            timezone=row["timezone"],
            latitude=float(row["latitude"]),
            longitude=float(row["longitude"]),
        )


@given('a city "{city_name}" with country "{country}" exists')
def step_city_with_country_exists(context, city_name: str, country: str):
    """Create a city with specified name and country."""
    City.objects.create(
        name=city_name,
        country=country,
        region="Test Region",
        timezone="UTC",
        latitude=0.0,
        longitude=0.0,
    )


@given('a city "{city_name}" with UUID "{city_uuid}" exists')
def step_city_with_uuid_exists(context, city_name: str, city_uuid: str):
    """Create a city with specified UUID."""
    City.objects.create(
        uuid=uuid.UUID(city_uuid),
        name=city_name,
        country="Test Country",
        region="Test Region",
        timezone="UTC",
        latitude=0.0,
        longitude=0.0,
    )


@when("the system retrieves the list of cities")
def step_system_retrieves_cities(context):
    """Retrieve all cities from the database."""
    context.cities = list(City.objects.all())


@when('searching for city with name "{city_name}"')
def step_search_city_by_name(context, city_name: str):
    """Search for a city by name."""
    try:
        context.city = City.objects.get(name=city_name)
    except City.DoesNotExist:
        context.city = None


@when('retrieving city by UUID "{city_uuid}"')
def step_retrieve_city_by_uuid(context, city_uuid: str):
    """Retrieve a city by UUID."""
    try:
        context.city = City.objects.get(uuid=uuid.UUID(city_uuid))
    except City.DoesNotExist:
        context.city = None


@then("exactly {count:d} cities are returned")
def step_verify_city_count(context, count: int):
    """Verify the number of cities returned."""
    assert len(context.cities) == count, f"Expected {count} cities, got {len(context.cities)}"


@then('the city "{city_name}" is returned with country "{country}"')
def step_verify_city_with_country(context, city_name: str, country: str):
    """Verify the city was found with correct country."""
    assert context.city is not None, f"City {city_name} not found"
    assert context.city.name == city_name, f"Expected name {city_name}, got {context.city.name}"
    assert (
        context.city.country == country
    ), f"Expected country {country}, got {context.city.country}"


@then('the city "{city_name}" is returned')
def step_verify_city_returned(context, city_name: str):
    """Verify the city was found."""
    assert context.city is not None, f"City {city_name} not found"
    assert context.city.name == city_name, f"Expected name {city_name}, got {context.city.name}"
