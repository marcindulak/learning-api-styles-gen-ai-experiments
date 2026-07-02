"""Steps for the service's web APIs (REST, GraphQL).

Scenario fixtures are created through the Django ORM, so they exist in
the behave test database. Relative URL paths are therefore resolved
against context.base_url — the behave-django live server backed by that
same test database. Absolute URLs keep pointing at the real service.
"""
from datetime import date, datetime, time, timedelta, timezone as dt_timezone

import parse
import requests
from behave import given, register_type, then, when
from django.core.exceptions import ValidationError
from django.utils import timezone

from weather.models import City, ForecastRecord, WeatherRecord


@parse.with_pattern(r'[^"]*')
def parse_quoted(text):
    return text


# A placeholder that cannot cross a quote boundary, so steps sharing the
# prefix 'a client sends a GET request to "..."' are not ambiguous.
register_type(Q=parse_quoted)

# Reference data for cities used in scenarios.
KNOWN_CITIES = {
    "Tokyo": {
        "country": "Japan",
        "region": "Asia",
        "timezone": "Asia/Tokyo",
        "latitude": 35.6762,
        "longitude": 139.6503,
    },
    "Delhi": {
        "country": "India",
        "region": "Asia",
        "timezone": "Asia/Kolkata",
        "latitude": 28.7041,
        "longitude": 77.1025,
    },
    "Shanghai": {
        "country": "China",
        "region": "Asia",
        "timezone": "Asia/Shanghai",
        "latitude": 31.2304,
        "longitude": 121.4737,
    },
    "Sao Paulo": {
        "country": "Brazil",
        "region": "South America",
        "timezone": "America/Sao_Paulo",
        "latitude": -23.5505,
        "longitude": -46.6333,
    },
    "Mexico City": {
        "country": "Mexico",
        "region": "North America",
        "timezone": "America/Mexico_City",
        "latitude": 19.4326,
        "longitude": -99.1332,
    },
    "Copenhagen": {
        "country": "Denmark",
        "region": "Europe",
        "timezone": "Europe/Copenhagen",
        "latitude": 55.6761,
        "longitude": 12.5683,
    },
}

GENERIC_CITY = {
    "country": "Unknown",
    "region": "Unknown",
    "timezone": "UTC",
    "latitude": 0.0,
    "longitude": 0.0,
}


def resolve_url(context, path):
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return f"{context.base_url}{path}"


def record_http_exchange(context, response):
    # Scenario-scoped log of HTTP exchanges, so multi-request scenarios
    # (e.g. NFR-003) can assert over every response of the scenario.
    if not hasattr(context, "http_exchanges"):
        context.http_exchanges = []
    context.http_exchanges.append(response)


def json_path(document, path):
    value = document
    for key in path.split("."):
        assert isinstance(value, dict) and key in value, (
            f'JSON path "{path}" not found at segment "{key}" in: {document}'
        )
        value = value[key]
    return value


@given('a city named "{name}" exists')
def step_city_exists(context, name):
    defaults = KNOWN_CITIES.get(name, GENERIC_CITY)
    city, _ = City.objects.get_or_create(name=name, defaults=defaults)
    context.city = city


@given(
    'a weather record for "{name}" exists with temperature {temperature:g}, '
    "humidity {humidity:g}, wind_speed {wind_speed:g}, pressure {pressure:g}, "
    "precipitation {precipitation:g}"
)
def step_weather_record_exists(
    context, name, temperature, humidity, wind_speed, pressure, precipitation
):
    city = City.objects.get(name=name)
    WeatherRecord.objects.create(
        city=city,
        observed_at=timezone.now(),
        temperature=temperature,
        humidity=humidity,
        wind_speed=wind_speed,
        pressure=pressure,
        precipitation=precipitation,
        source="test-fixture",
    )


@given('weather records for "{name:Q}" exist for each day from "{start:Q}" to "{end:Q}"')
def step_weather_records_for_date_range(context, name, start, end):
    city = City.objects.get(name=name)
    day = date.fromisoformat(start)
    last = date.fromisoformat(end)
    while day <= last:
        WeatherRecord.objects.create(
            city=city,
            observed_at=datetime.combine(day, time(hour=12), tzinfo=dt_timezone.utc),
            temperature=20.0,
            humidity=60.0,
            wind_speed=3.0,
            pressure=1013.0,
            precipitation=0.0,
            source="test-fixture",
        )
        day += timedelta(days=1)


@given('forecast records for "{name:Q}" exist for the next 7 days')
def step_forecast_records_next_seven_days(context, name):
    city = City.objects.get(name=name)
    today = timezone.localdate()
    for day in range(1, 8):
        ForecastRecord.objects.get_or_create(
            city=city,
            forecast_date=today + timedelta(days=day),
            defaults={
                "temperature_min": 15.0,
                "temperature_max": 25.0,
                "source": "test-fixture",
            },
        )


@when(
    'an attempt is made to store a forecast record for "{name:Q}" '
    "with a forecast_date {days:d} days from today"
)
def step_attempt_store_forecast(context, name, days):
    city = City.objects.get(name=name)
    context.forecast_validation_error = None
    try:
        ForecastRecord.objects.create(
            city=city,
            forecast_date=timezone.localdate() + timedelta(days=days),
            temperature_min=15.0,
            temperature_max=25.0,
            source="test-fixture",
        )
    except ValidationError as error:
        context.forecast_validation_error = error


@then("the forecast record is rejected with a validation error")
def step_forecast_rejected(context):
    assert context.forecast_validation_error is not None, (
        "expected a ValidationError, but the forecast record was stored"
    )


@then('"{name:Q}" has {count:d} forecast records')
def step_city_forecast_record_count(context, name, count):
    city = City.objects.get(name=name)
    actual = city.forecast_records.count()
    assert actual == count, (
        f"expected {count} forecast records for {name}, got {actual}"
    )


@then('every record has a "{field:Q}" within {days:d} days from today')
def step_every_record_date_within_days(context, field, days):
    records = context.response.json()["results"]
    assert records, "no records in the response to check dates of"
    today = timezone.localdate()
    horizon = today + timedelta(days=days)
    for record in records:
        value = date.fromisoformat(record[field])
        assert today <= value <= horizon, (
            f"record {field}={record[field]} is outside [{today}, {horizon}]"
        )


@then("the response JSON contains an error message mentioning the maximum of 7 days")
def step_response_mentions_seven_day_maximum(context):
    body = context.response.text
    assert "maximum" in body and "7" in body and "day" in body, (
        f"response does not mention the maximum of 7 days: {body}"
    )


@when('a client sends a GET request to "{path:Q}"')
def step_get_request(context, path):
    context.response = requests.get(resolve_url(context, path), timeout=10)
    record_http_exchange(context, context.response)


@when('a client sends a GET request to "{path:Q}" for the city "{name:Q}"')
def step_get_request_for_city(context, path, name):
    city = City.objects.get(name=name)
    path = path.replace("<city_uuid>", str(city.uuid))
    context.response = requests.get(resolve_url(context, path), timeout=10)


@when(
    'a client sends a GraphQL query for the current weather of "{name}" '
    'to "{path}" requesting fields "{fields}"'
)
def step_graphql_weather_query(context, name, path, fields):
    query = f'{{ weather(cityName: "{name}") {{ {fields} }} }}'
    context.response = requests.post(
        resolve_url(context, path), json={"query": query}, timeout=10
    )


@then('the response content type is "{expected}"')
def step_response_content_type(context, expected):
    actual = context.response.headers.get("Content-Type", "")
    assert actual.startswith(expected), (
        f'expected content type "{expected}", got "{actual}"'
    )


@then('the response JSON contains the field "{field}" with value {expected:g}')
def step_response_json_field_number(context, field, expected):
    body = context.response.json()
    assert field in body, f'field "{field}" not in response JSON: {body}'
    actual = body[field]
    assert actual == expected, f"expected {field}={expected}, got {actual}"


@then(
    'the response JSON field "{field}" contains an entry '
    'with "{key}" equal to "{value}"'
)
def step_response_json_list_entry(context, field, key, value):
    body = context.response.json()
    assert field in body, f'field "{field}" not in response JSON: {body}'
    entries = [entry for entry in body[field] if entry.get(key) == value]
    assert entries, f'no entry with {key}="{value}" in "{field}": {body[field]}'
    context.matched_entry = entries[0]


@then('that entry contains a non-empty "{field}" field')
def step_matched_entry_non_empty_field(context, field):
    entry = context.matched_entry
    assert entry.get(field), f'entry field "{field}" is empty or missing: {entry}'


@then('the response JSON field "{field:Q}" contains exactly {count:d} records')
def step_response_json_field_record_count(context, field, count):
    body = context.response.json()
    assert field in body, f'field "{field}" not in response JSON: {body}'
    actual = len(body[field])
    assert actual == count, (
        f'expected exactly {count} records in "{field}", got {actual}: {body[field]}'
    )


@then('the response JSON field "{field:Q}" contains exactly {count:d} record')
def step_response_json_field_record_count_singular(context, field, count):
    step_response_json_field_record_count(context, field, count)


@then('every record has an "{field:Q}" timestamp between "{start:Q}" and "{end:Q}"')
def step_every_record_timestamp_between(context, field, start, end):
    records = context.response.json()["results"]
    assert records, "no records in the response to check timestamps of"
    lower = datetime.fromisoformat(start.replace("Z", "+00:00"))
    upper = datetime.fromisoformat(end.replace("Z", "+00:00"))
    for record in records:
        observed = datetime.fromisoformat(record[field].replace("Z", "+00:00"))
        assert lower <= observed <= upper, (
            f'record {field}={record[field]} is outside [{start}, {end}]'
        )


@then('the records are ordered by "{field:Q}" ascending')
def step_records_ordered_ascending(context, field):
    records = context.response.json()["results"]
    values = [record[field] for record in records]
    assert values == sorted(values), f'records are not ordered by "{field}": {values}'


@then('the response JSON path "{path}" equals {expected:g}')
def step_response_json_path_equals(context, path, expected):
    body = context.response.json()
    actual = json_path(body, path)
    assert actual == expected, f'expected JSON path "{path}"={expected}, got {actual}'
