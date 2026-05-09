"""Step definitions for FR-006: Weather historical data.

Adds three steps used by the FR-006 scenarios:

* ``a weather record for "..." on "..." with temperature N exists`` —
  inserts a :class:`WeatherRecord` for the named city on the named date
  with the given temperature. Other reading fields are left null because
  the FR-006 scenarios do not assert them.

* ``the response body has a key "..." with the value "..."`` — exact
  string match on a JSON path of the form ``results[0].observed_on``.

* ``the response body has a key "..." with an empty list`` — asserts
  the value at the JSON path is a list of length zero.

Reused steps from earlier features:

* ``the service is running`` (FR-007).
* ``a city named "..." exists`` (FR-011).
* ``a client sends GET to "..."`` (FR-009).
* ``the response status is N`` (FR-007).
* ``the response body has a key "..." with the value N`` (FR-009, now
  generalised to floats and dotted/indexed paths).
"""

from __future__ import annotations

import datetime
import json

from behave import given, then


def _decode_json(context):
    """Parse the latest response body as JSON, caching it on the context."""

    if not hasattr(context, "response_json") or context.response_json is None:
        context.response_json = json.loads(
            context.response.content.decode("utf-8")
        )
    return context.response_json


def _resolve_path(body, key: str):
    """Walk a dotted/indexed key path like ``results[0].observed_on``.

    Supports two segment forms: a bare attribute name (``results``) and
    an indexed name (``results[0]``). Raises ``KeyError`` with a helpful
    message if the path cannot be resolved.
    """

    current = body
    for segment in key.split("."):
        index = None
        if "[" in segment and segment.endswith("]"):
            attr, _, rest = segment.partition("[")
            index = int(rest[:-1])
        else:
            attr = segment
        if not isinstance(current, dict) or attr not in current:
            raise KeyError(
                f"Cannot resolve {key!r}: missing {attr!r} in {current!r}."
            )
        current = current[attr]
        if index is not None:
            if not isinstance(current, list) or index >= len(current):
                raise KeyError(
                    f"Cannot resolve {key!r}: index {index} out of range "
                    f"in {current!r}."
                )
            current = current[index]
    return current


@given(
    'a weather record for "{name}" on "{observed_on}" with temperature {temperature:g} exists'
)
def step_weather_record_exists(
    context, name: str, observed_on: str, temperature: float
) -> None:
    from cities.models import City, WeatherRecord

    city = City.objects.get(name=name)
    WeatherRecord.objects.update_or_create(
        city=city,
        observed_on=datetime.date.fromisoformat(observed_on),
        defaults={"temperature": temperature},
    )


@then('the response body has a key "{key}" with the value "{expected}"')
def step_response_key_string_value(context, key: str, expected: str) -> None:
    body = _decode_json(context)
    actual = _resolve_path(body, key)
    assert actual == expected, (
        f"Expected {key}={expected!r}, got {actual!r}."
    )


@then('the response body has a key "{key}" with an empty list')
def step_response_key_empty_list(context, key: str) -> None:
    body = _decode_json(context)
    value = _resolve_path(body, key)
    assert isinstance(value, list), (
        f"Expected a list at {key!r}, got {type(value).__name__}: {value!r}."
    )
    assert len(value) == 0, (
        f"Expected empty list at {key!r}, got length {len(value)}: {value!r}."
    )
