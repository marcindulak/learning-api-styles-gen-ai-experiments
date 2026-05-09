"""Step definitions for FR-009: Weather data limited to the 5 biggest cities.

Reuses the ``the service is running`` and ``the response status is N``
steps from FR-007. Adds steps for inspecting JSON response bodies, for
authenticating an admin via Django session login, and for asserting
that the seed migration has registered the five supported cities.

The test client used here is :class:`django.test.Client` (created in
``features/environment.py``). DRF accepts session authentication out of
the box, so a successful ``client.login`` is enough to exercise the
admin-only POST endpoint without standing up JWT.
"""

from __future__ import annotations

import json

from behave import given, then, when


def _decode_json(context):
    """Parse the latest response body as JSON, caching it on the context."""

    if not hasattr(context, "response_json"):
        context.response_json = json.loads(
            context.response.content.decode("utf-8")
        )
    return context.response_json


@given('the 5 supported cities are already registered')
def step_five_cities_registered(context) -> None:
    # The data migration ``cities/migrations/0002_seed_cities`` populates
    # the five rows; this step is an explicit precondition assertion so a
    # missing or altered migration surfaces with a clear failure message.
    from cities.models import SUPPORTED_CITY_LIMIT, City

    actual = City.objects.count()
    assert actual == SUPPORTED_CITY_LIMIT, (
        f"Expected {SUPPORTED_CITY_LIMIT} seeded cities, found {actual}."
    )


@given('the user is authenticated as admin')
def step_authenticated_as_admin(context) -> None:
    from django.contrib.auth import get_user_model

    user_model = get_user_model()
    # Use a fixed username/password pair scoped to this scenario only;
    # the surrounding ``before_scenario`` transaction rolls it back.
    user_model.objects.create_superuser(username="admin", password="admin-pass")
    logged_in = context.client.login(username="admin", password="admin-pass")
    assert logged_in, "Admin session login failed."


@when('a client sends GET to "{path}"')
def step_client_get(context, path: str) -> None:
    context.response = context.client.get(path)
    context.response_json = None
    if hasattr(context, "response_json"):
        del context.response_json


@when('the admin sends POST to "{path}" with a payload for a city named "{name}"')
def step_admin_post_city(context, path: str, name: str) -> None:
    # Body mirrors the example payload in REQUIREMENTS.md so the test
    # exercises the same shape an end-to-end curl would send.
    payload = {
        "name": name,
        "country": "Denmark",
        "region": "Europe",
        "timezone": "Europe/Copenhagen",
        "latitude": "55.676100",
        "longitude": "12.568300",
    }
    context.response = context.client.post(
        path,
        data=json.dumps(payload),
        content_type="application/json",
    )
    if hasattr(context, "response_json"):
        del context.response_json


@then('the response body has a key "{key}" with the value {value:d}')
def step_response_key_int(context, key: str, value: int) -> None:
    body = _decode_json(context)
    assert key in body, f"Key {key!r} not found; body keys: {list(body)}"
    assert body[key] == value, (
        f"Expected {key}={value}, got {body[key]!r}."
    )


@then('the response body has a key "{key}" with a value containing "{substring}"')
def step_response_key_substring(context, key: str, substring: str) -> None:
    body = _decode_json(context)
    assert key in body, f"Key {key!r} not found; body keys: {list(body)}"
    actual = body[key]
    assert substring in str(actual), (
        f"Expected substring {substring!r} in {key}={actual!r}."
    )


@then('the response body has a key "results" listing exactly the city names {names}')
def step_results_city_names(context, names: str) -> None:
    # ``names`` is the raw Gherkin tail starting with the first quote, e.g.
    #   "Tokyo", "Delhi", "Shanghai", "Sao Paulo", "Mexico City"
    # Parse it by splitting on quote pairs to avoid pulling in a regex.
    expected = {chunk for chunk in names.split('"') if chunk.strip(", ")}
    body = _decode_json(context)
    assert "results" in body, f"No 'results' key; body keys: {list(body)}"
    actual = {row["name"] for row in body["results"]}
    assert actual == expected, (
        f"Expected city names {sorted(expected)}, got {sorted(actual)}."
    )
