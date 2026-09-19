import json

from behave import given, then, when
from common_steps import CITY_DEFAULTS, _client_for, _response_body

from weather.models import City, WeatherRecord


def _graphql_data(context, path):
    data = _response_body(context)["data"]
    for part in path.split("."):
        data = data[part]
    return data


def _coerce(value):
    # A quoted literal like `"Clear"` is a string, `true`/`false` is a bool
    # (FR-007's "stale" field), and anything else is a number.
    if value in ("true", "false"):
        return value == "true"
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    return float(value)


def _parse_field_list(text):
    # Turns "temperature, humidity, and condition" into ["temperature", "humidity", "condition"].
    fields = []
    for part in text.split(","):
        part = part.strip()
        if part.startswith("and "):
            part = part[len("and "):]
        fields.append(part)
    return fields


@given('the city "{name}" exists with uuid "{uuid}"')
def step_given_city_with_uuid(context, name, uuid):
    City.objects.get_or_create(uuid=uuid, defaults={"name": name, **CITY_DEFAULTS})


@given(
    '"{name}" has a current weather record with temperature {temperature:g}, humidity {humidity:d}, '
    'wind_speed {wind_speed:g}, precipitation_probability {precipitation_probability:d}, and condition "{condition}"'
)
def step_given_current_weather_record(context, name, temperature, humidity, wind_speed, precipitation_probability, condition):
    WeatherRecord.objects.create(
        city=City.objects.get(name=name),
        temperature=temperature,
        humidity=humidity,
        wind_speed=wind_speed,
        precipitation_probability=precipitation_probability,
        condition=condition,
    )


@then('the response body contains "{field}" equal to {value}')
def step_then_body_field_equals(context, field, value):
    assert _response_body(context)[field] == _coerce(value)


@when('a client sends a "POST /api/graphql" query requesting {fields} for city uuid "{uuid}"')
def step_when_sends_graphql_query(context, fields, uuid):
    query = "query($cityUuid: String!) { currentWeather(cityUuid: $cityUuid) { %s } }" % " ".join(
        _parse_field_list(fields)
    )
    context.last_response = _client_for(context, "anonymous").post(
        "/api/graphql",
        data=json.dumps({"query": query, "variables": {"cityUuid": uuid}}),
        content_type="application/json",
    )


@then('the GraphQL response field "{path}" equals {value}')
def step_then_graphql_field_equals(context, path, value):
    assert _graphql_data(context, path) == _coerce(value)


@then('the GraphQL response field "{path}" is null')
def step_then_graphql_field_is_null(context, path):
    assert _graphql_data(context, path) is None


@then('the GraphQL response contains an "{field}" field')
def step_then_graphql_contains_field(context, field):
    assert field in _response_body(context)
