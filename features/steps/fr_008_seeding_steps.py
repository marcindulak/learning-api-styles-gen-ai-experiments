import json

from behave import given, then, when
from common_steps import CITY_DEFAULTS, FakeWeatherProvider, _client_for

from weather.models import City, WeatherRecord
from weather.providers import WeatherReading
from weather.services import BIGGEST_CITIES, seed_cities

SEEDED_CITY_NAMES = [city["name"] for city in BIGGEST_CITIES]

# FR-008's scenarios only assert that a current weather record exists after
# seeding, never its content, so the same canned reading is used for all 5
# cities rather than one per city.
_SEED_READING = WeatherReading(
    temperature=20.0, humidity=50, wind_speed=10.0, precipitation_probability=0, condition="Clear",
)


def _seed_provider():
    provider = FakeWeatherProvider()
    for name in SEEDED_CITY_NAMES:
        provider.readings[name] = _SEED_READING
    return provider


@given("the service starts for the first time with an empty database")
def step_given_empty_database(context):
    assert City.objects.count() == 0


@when("startup seeding completes")
def step_when_seeding_completes(context):
    seed_cities(_seed_provider())


@then('cities named "Tokyo", "Delhi", "Shanghai", "São Paulo", and "Mexico City" exist')
def step_then_five_cities_exist(context):
    for name in SEEDED_CITY_NAMES:
        assert City.objects.filter(name=name).exists()


@then("each of these 5 cities has a current weather record")
def step_then_five_cities_have_weather(context):
    for name in SEEDED_CITY_NAMES:
        assert WeatherRecord.objects.filter(city__name=name).exists()


@given("the 5 seeded cities already exist")
def step_given_five_seeded_cities(context):
    seed_cities(_seed_provider())


@when('an admin creates a city named "{name}" via "POST /api/cities"')
def step_when_admin_creates_city(context, name):
    payload = {"name": name, **CITY_DEFAULTS}
    context.last_response = _client_for(context, "admin").post(
        "/api/cities", data=json.dumps(payload), content_type="application/json"
    )


@then('"{name}" has no current weather record until a subsequent provider poll stores one')
def step_then_no_weather_record_yet(context, name):
    assert not WeatherRecord.objects.filter(city__name=name).exists()
