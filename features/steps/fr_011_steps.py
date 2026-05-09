"""Step definitions for FR-011: Admin and regular user with object-level
permissions.

Adds JWT-flavoured When/Then steps on top of the user-creation Givens
already defined for FR-007. The flow exercised here mirrors the curl
example in REQUIREMENTS.md: a client first POSTs credentials to
``/api/jwt/obtain`` to receive a Bearer token, then sends authenticated
requests with ``Authorization: Bearer <access>``.

The "actor" of a step can take two surface forms in the feature file:

* The bare phrase ``the admin`` (resolved against
  ``context.admin_username``).
* A quoted username such as ``"alice"`` (used verbatim).

Both forms route through :func:`_resolve_actor` so the implementation
stays in one place.
"""

from __future__ import annotations

import json

from behave import given, then, when


# Sample city payload reused by every "valid city payload" step. Mirrors
# the example body in REQUIREMENTS.md so the test exercises the same
# shape as a hand-run curl invocation. Copenhagen is intentional: it is
# not in the FR-009 supported set, so the request only succeeds if the
# admin path bypasses the city-limit check (which it does not — the
# scenario asserts only the auth/permission outcome, not the eventual
# 201 vs 400; the seed leaves 5 rows in place so any admin POST trips
# the FR-009 cap, but FR-011 scenario 1 deletes one row first to leave
# room — see ``_make_room_for_one_city``).
VALID_CITY_PAYLOAD = {
    "name": "Copenhagen",
    "country": "Denmark",
    "region": "Europe",
    "timezone": "Europe/Copenhagen",
    "latitude": "55.676100",
    "longitude": "12.568300",
}


def _resolve_actor(context, actor: str) -> str:
    """Map a feature-file actor label to a username.

    ``the admin`` resolves to whatever username the previous Given step
    registered as ``context.admin_username``. Any other value is treated
    as a literal username (the FR-011 feature quotes them as e.g.
    ``"alice"`` and the parser strips the quotes).
    """

    if actor == "the admin":
        return context.admin_username
    return actor


def _obtain_jwt(context, username: str, path: str) -> None:
    password = context.credentials[username]
    response = context.client.post(
        path,
        data=json.dumps({"username": username, "password": password}),
        content_type="application/json",
    )
    assert response.status_code == 200, (
        f"JWT obtain for {username!r} failed: status {response.status_code}, "
        f"body {response.content!r}"
    )
    context.access_token = json.loads(response.content)["access"]


def _make_room_for_one_city() -> None:
    """Delete one seeded city so a valid POST does not trip FR-009's cap.

    FR-011 scenario 1 asserts that an admin's POST to ``/api/cities``
    succeeds with HTTP 201. The seed inserts the five supported cities,
    which means a sixth row would otherwise be rejected by the FR-009
    city-limit check before the auth/permission outcome FR-011 cares
    about can be reached. Removing one seeded row first keeps the test
    focused on FR-011 (auth) without weakening FR-009.
    """

    from cities.models import City

    City.objects.filter(name="Tokyo").delete()


@when('the admin obtains a JWT access token via POST to "{path}"')
def step_admin_obtains_jwt(context, path: str) -> None:
    username = _resolve_actor(context, "the admin")
    _obtain_jwt(context, username, path)


@when('"{username}" obtains a JWT access token via POST to "{path}"')
def step_user_obtains_jwt(context, username: str, path: str) -> None:
    _obtain_jwt(context, username, path)


@when('the admin sends POST to "/api/cities" with a valid city payload using the access token')
def step_admin_post_city_with_token(context) -> None:
    _make_room_for_one_city()
    context.response = context.client.post(
        "/api/cities",
        data=json.dumps(VALID_CITY_PAYLOAD),
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {context.access_token}",
    )


@when('"{username}" sends POST to "/api/cities" with a valid city payload using the access token')
def step_user_post_city_with_token(context, username: str) -> None:
    context.response = context.client.post(
        "/api/cities",
        data=json.dumps(VALID_CITY_PAYLOAD),
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {context.access_token}",
    )


@when('an anonymous client sends POST to "/api/cities" with a valid city payload')
def step_anonymous_post_city(context) -> None:
    # APIClient instance from before_scenario carries no credentials by
    # default, so this is already anonymous; we still construct a fresh
    # client to make the intent explicit and to avoid accidentally
    # picking up a session cookie from an earlier step in the same
    # scenario.
    from rest_framework.test import APIClient

    fresh_client = APIClient()
    context.response = fresh_client.post(
        "/api/cities",
        data=json.dumps(VALID_CITY_PAYLOAD),
        content_type="application/json",
    )


@when('"{username}" sends GET to "{path}" using the access token')
def step_user_get_with_token(context, username: str, path: str) -> None:
    context.response = context.client.get(
        path,
        HTTP_AUTHORIZATION=f"Bearer {context.access_token}",
    )


@given('a city named "{name}" exists')
def step_city_named_exists(context, name: str) -> None:
    """Assert (and ensure) the named city is in the database.

    The five FR-009 cities are re-seeded in ``before_scenario`` so this
    step is a no-op for them; for any other name it inserts a placeholder
    row. The placeholder values are deliberately empty/zero — FR-011 only
    needs the row to exist, not its weather attributes.
    """

    from cities.models import City

    City.objects.get_or_create(
        name=name,
        defaults={
            "country": "",
            "region": "",
            "timezone": "UTC",
            "latitude": 0,
            "longitude": 0,
        },
    )
