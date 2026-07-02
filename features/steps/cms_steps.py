"""Steps for the content management system (the Django admin site).

CMS logins use a requests.Session against context.base_url — the
behave-django live server backed by the test database where the user
fixtures from auth_steps.py exist. Django's admin login form is CSRF
protected, so each form POST first fetches the page to obtain the token.
"""
import re

import parse
import requests
from behave import given, register_type, then, when


@parse.with_pattern(r'[^"]*')
def parse_quoted(text):
    return text


# Registered here as well: importing it from a sibling step module would
# re-execute that module and register duplicate steps.
register_type(Q=parse_quoted)

CSRF_INPUT_RE = re.compile(r'name="csrfmiddlewaretoken" value="([^"]+)"')


def csrf_token_from(response):
    match = CSRF_INPUT_RE.search(response.text)
    assert match, f"no csrfmiddlewaretoken input found on {response.url}"
    return match.group(1)


def cms_login(context, path, username, password):
    """Log in through the admin login form and return the final response."""
    session = requests.Session()
    login_page = session.get(f"{context.base_url}{path}", timeout=10)
    assert login_page.status_code == 200, (
        f"CMS login page returned {login_page.status_code}"
    )
    response = session.post(
        login_page.url,
        data={
            "username": username,
            "password": password,
            "csrfmiddlewaretoken": csrf_token_from(login_page),
            "next": path,
        },
        timeout=10,
    )
    context.cms_session = session
    context.response = response
    return response


@when(
    'the admin user logs in to "{path:Q}" with '
    'username "{username:Q}" and password "{password:Q}"'
)
def step_admin_logs_in(context, path, username, password):
    response = cms_login(context, path, username, password)
    assert "Site administration" in response.text, (
        f"admin CMS login did not reach the index page (status "
        f"{response.status_code}): {response.text[:500]}"
    )


@when(
    'the regular user attempts to log in to "{path:Q}" with '
    'username "{username:Q}" and password "{password:Q}"'
)
def step_regular_user_attempts_login(context, path, username, password):
    cms_login(context, path, username, password)


@given("the admin user is logged in to the CMS")
def step_admin_is_logged_in(context):
    credentials = context.credentials["admin"]
    response = cms_login(
        context, "/admin/", credentials["username"], credentials["password"]
    )
    assert "Site administration" in response.text, (
        f"admin CMS login failed (status {response.status_code})"
    )


@when(
    'the admin user submits the CMS add-city form with name "{name:Q}", '
    'country "{country:Q}", region "{region:Q}", timezone "{tz:Q}", '
    "latitude {latitude:g} and longitude {longitude:g}"
)
def step_admin_submits_add_city_form(
    context, name, country, region, tz, latitude, longitude
):
    session = context.cms_session
    add_page = session.get(f"{context.base_url}/admin/weather/city/add/", timeout=10)
    assert add_page.status_code == 200, (
        f"CMS add-city page returned {add_page.status_code}"
    )
    context.response = session.post(
        add_page.url,
        data={
            "name": name,
            "country": country,
            "region": region,
            "timezone": tz,
            "latitude": latitude,
            "longitude": longitude,
            "csrfmiddlewaretoken": csrf_token_from(add_page),
            "_save": "Save",
        },
        timeout=10,
    )
    assert context.response.status_code == 200, (
        f"CMS add-city submission returned {context.response.status_code}"
    )


@then('the response body contains "{text:Q}"')
def step_response_body_contains(context, text):
    assert text in context.response.text, (
        f'"{text}" not found in response body: {context.response.text[:500]}'
    )


@then('the CMS index page lists a section for "{section:Q}"')
def step_cms_lists_section(context, section):
    assert section in context.response.text, (
        f'CMS index page has no "{section}" section'
    )


@then("the CMS login is rejected with an authentication error message")
def step_cms_login_rejected(context):
    body = context.response.text
    assert "Site administration" not in body, (
        "CMS login unexpectedly succeeded for a non-staff user"
    )
    assert "errornote" in body and "Please enter the correct" in body, (
        f"no authentication error message on the login page: {body[:500]}"
    )
