import logging
from datetime import timedelta

from behave import given, then, when
from common_steps import FakeWeatherProvider
from django.utils import timezone

from weather.models import City, WeatherRecord
from weather.providers import OpenMeteoWeatherProvider, WeatherReading
from weather.services import poll_city_weather


def _provider(context):
    if not hasattr(context, "weather_provider"):
        context.weather_provider = FakeWeatherProvider()
    return context.weather_provider


@given('the weather data provider returns a reading for "{name}" with temperature {temperature:g} and condition "{condition}"')
def step_given_provider_reading(context, name, temperature, condition):
    _provider(context).readings[name] = WeatherReading(
        temperature=temperature,
        humidity=50,
        wind_speed=10.0,
        precipitation_probability=0,
        condition=condition,
    )


@given("the weather data provider is unavailable")
@given("the weather data provider has been unavailable for the last {_hours:d} hours")
def step_given_provider_unavailable(context, _hours=None):
    # _hours is narrative only: staleness (see the "last refreshed ... ago"
    # step below) is derived purely from recorded_at, not from how long the
    # provider itself has been down.
    _provider(context).available = False


@given('"{name}" has a stored weather record with temperature {temperature:g} last refreshed {amount:d} {unit:w} ago')
def step_given_weather_record_refreshed_ago(context, name, temperature, amount, unit):
    if unit.startswith("hour"):
        age = timedelta(hours=amount)
    elif unit.startswith("minute"):
        age = timedelta(minutes=amount)
    else:
        raise ValueError(f"unrecognized time unit: {unit}")
    # Not reusing fr_001's step_given_current_weather_record here: its
    # Gherkin text has no way to express a backdated recorded_at or a
    # source, both of which this step needs to control directly.
    WeatherRecord.objects.create(
        city=City.objects.get(name=name),
        temperature=temperature,
        humidity=50,
        wind_speed=10.0,
        precipitation_probability=0,
        condition="Clear",
        recorded_at=timezone.now() - age,
        source=OpenMeteoWeatherProvider.name,
    )


@given('"{name}" already has a stored weather record with temperature {temperature:g}')
def step_given_existing_weather_record(context, name, temperature):
    step_given_weather_record_refreshed_ago(context, name, temperature, amount=0, unit="hours")


@when('the service polls the weather data provider for "{name}"')
def step_when_polls(context, name):
    context.last_polled_city = name
    # Captures log records emitted by weather.services during the poll, so
    # the "failed poll is logged" Then step can assert on them without a
    # mocking library.
    records = []
    handler = logging.Handler()
    handler.emit = records.append
    logger = logging.getLogger("weather.services")
    logger.addHandler(handler)
    try:
        poll_city_weather(City.objects.get(name=name), _provider(context))
    finally:
        logger.removeHandler(handler)
    context.poll_log_records = records


def _latest_record(name):
    return WeatherRecord.objects.filter(city__name=name).latest()


@then('a weather record for "{name}" is stored with temperature {temperature:g} and condition "{condition}"')
def step_then_weather_record_stored(context, name, temperature, condition):
    record = _latest_record(name)
    assert record.temperature == temperature
    assert record.condition == condition


@then("the stored record's source is the weather data provider")
def step_then_stored_record_source(context):
    assert _latest_record(context.last_polled_city).source == OpenMeteoWeatherProvider.name


@then('the current weather record for "{name}" still has temperature {temperature:g}')
def step_then_current_weather_unchanged(context, name, temperature):
    assert _latest_record(name).temperature == temperature


@then("the failed poll is logged")
def step_then_failed_poll_logged(context):
    assert any(record.levelno >= logging.WARNING for record in context.poll_log_records)


@then("every returned indicator value originates from a weather record stored via the weather data provider")
def step_then_no_fabricated_data(context):
    # No weather record was ever stored for this city in this scenario, so
    # the only way this invariant can hold is if the endpoint returns 404
    # rather than falling back to a fabricated/default reading.
    assert context.last_response.status_code == 404
