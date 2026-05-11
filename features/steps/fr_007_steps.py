"""Step definitions for FR-007: Content Management System for admin.

Verifies the Django admin behaviour required by FR-007: an admin (staff)
user can sign in and reach the admin index, a regular non-staff user is
rejected at /admin/login/ with the standard staff-account error message,
and an anonymous request to /admin/ is redirected to the login page.

Steps interact with Django via :class:`django.test.Client`, which dispatches
requests through the WSGI stack without a network listener. The client is
created in ``features/environment.py`` (one per scenario) so the session
cookie persists across the When/Then steps that simulate the same browser.
"""

from __future__ import annotations

from behave import given, then, when


@given('the service is running')
def step_service_running(context) -> None:
    """Assert the Django stack was bootstrapped by ``before_all``.

    "the service is running" in the BDD context means Django is configured,
    migrations have been applied to the test database, and a test ``Client``
    is ready to dispatch requests. There is no separate HTTP listener: the
    Django test client invokes the WSGI application in-process.
    """

    assert getattr(context, "django_ready", False), (
        "Django is not bootstrapped. Ensure src/ exists and Django is installed."
    )
    assert hasattr(context, "client"), "Test client was not initialised."


def _remember_credentials(context, username: str, password: str) -> None:
    # Stash username/password so a later step (e.g. FR-011's JWT obtain)
    # can authenticate the same user without the feature having to repeat
    # the password literal in every When clause.
    if not hasattr(context, "credentials"):
        context.credentials = {}
    context.credentials[username] = password


@given('an admin user with username "{username}" and password "{password}" exists')
def step_admin_user_exists(context, username: str, password: str) -> None:
    from django.contrib.auth import get_user_model

    user_model = get_user_model()
    user_model.objects.create_superuser(username=username, password=password)
    _remember_credentials(context, username, password)
    # FR-011 scenarios refer to the admin without a username
    # ("the admin obtains a JWT..."); track which user is the admin so the
    # bare-actor step does not need to re-parse the previous Given.
    context.admin_username = username


@given('a regular user with username "{username}" and password "{password}" exists')
def step_regular_user_exists(context, username: str, password: str) -> None:
    from django.contrib.auth import get_user_model

    user_model = get_user_model()
    user_model.objects.create_user(username=username, password=password)
    _remember_credentials(context, username, password)


@when('a browser session sends POST to "{path}" with username "{username}" and password "{password}"')
def step_browser_post_login(context, path: str, username: str, password: str) -> None:
    # follow=True so we land on the post-redirect page when the credentials
    # are valid; that lets the same step assert either a redirected admin
    # index or the re-rendered login form for a non-staff user.
    context.response = context.client.post(
        path,
        data={"username": username, "password": password},
        follow=True,
    )


@when('the browser session sends GET to "{path}"')
def step_browser_get(context, path: str) -> None:
    context.response = context.client.get(path)


@when('a client sends GET to "{path}" without an active session')
def step_anonymous_get(context, path: str) -> None:
    from django.test import Client

    # A fresh client guarantees no session cookie from any earlier step.
    fresh_client = Client()
    context.response = fresh_client.get(path)


@then('the response status is {status:d}')
def step_response_status(context, status: int) -> None:
    actual = context.response.status_code
    assert actual == status, f"Expected status {status}, got {actual}."


@then('the response body contains the substring "{substring}"')
def step_response_body_contains(context, substring: str) -> None:
    body = context.response.content.decode("utf-8", errors="replace")
    assert substring in body, (
        f"Expected response body to contain {substring!r}; "
        f"first 500 chars were: {body[:500]!r}"
    )


@then('the response Location header starts with "{prefix}"')
def step_response_location_prefix(context, prefix: str) -> None:
    location = context.response.headers.get("Location", "")
    assert location.startswith(prefix), (
        f"Expected Location header to start with {prefix!r}, got {location!r}."
    )
