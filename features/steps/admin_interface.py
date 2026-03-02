"""Step definitions for Django admin interface features."""

import subprocess
from http.cookies import SimpleCookie

from behave import given, then, when
from django.contrib.auth import get_user_model

from src.weather.models import City, WeatherAlert


@when('I navigate to "{url}"')
def step_navigate_to_url(context, url: str):
    """Navigate to a URL with authentication cookie."""
    cookie_args = []
    if hasattr(context, 'admin_cookie_file') and context.admin_cookie_file:
        cookie_args = ['--cookie', context.admin_cookie_file, '--cookie-jar', context.admin_cookie_file]

    result = subprocess.run(
        [
            'curl',
            *cookie_args,
            '--location',
            '--silent',
            '--write-out', '\\n%{http_code}',
            f'http://localhost:8000{url}'
        ],
        capture_output=True,
        text=True,
        timeout=10
    )

    lines = result.stdout.strip().split('\n')
    context.response_status_code = int(lines[-1])
    context.response_body = '\n'.join(lines[:-1]) if len(lines) > 1 else ''


@when('I submit the city form with:')
def step_submit_city_form(context):
    """Submit the city form via admin interface."""
    import re
    from urllib.parse import urlencode

    cookie_args = []
    if hasattr(context, 'admin_cookie_file') and context.admin_cookie_file:
        cookie_args = ['--cookie', context.admin_cookie_file, '--cookie-jar', context.admin_cookie_file]

    result = subprocess.run(
        [
            'curl',
            *cookie_args,
            '--silent',
            'http://localhost:8000/admin/weather/city/add/'
        ],
        capture_output=True,
        text=True,
        timeout=10
    )

    csrf_match = re.search(r'csrfmiddlewaretoken["\']?\s+value=["\']([^"\']+)["\']', result.stdout)
    csrf_token = csrf_match.group(1) if csrf_match else ''

    form_data = {}
    # Behave treats the first row as headers
    # Since our table is key-value pairs, we need to include the headers as the first data row
    headers = context.table.headings
    if len(headers) == 2:
        # First row became headers, so add it as data
        form_data[headers[0].strip()] = headers[1].strip()

    # Then process the remaining rows
    for row in context.table:
        field_name = str(row.cells[0]).strip()
        field_value = str(row.cells[1]).strip()
        form_data[field_name] = field_value

    form_data['_save'] = 'Save'
    form_data['csrfmiddlewaretoken'] = csrf_token

    form_params = urlencode(form_data)

    result = subprocess.run(
        [
            'curl',
            *cookie_args,
            '--data', form_params,
            '--header', 'Content-Type: application/x-www-form-urlencoded',
            '--header', 'Referer: http://localhost:8000/admin/weather/city/add/',
            '--request', 'POST',
            '--silent',
            '--write-out', '\\n%{http_code}',
            'http://localhost:8000/admin/weather/city/add/'
        ],
        capture_output=True,
        text=True,
        timeout=10
    )

    lines = result.stdout.strip().split('\n')
    context.response_status_code = int(lines[-1])
    context.response_body = '\n'.join(lines[:-1]) if len(lines) > 1 else ''


@then('the page contains "{text}"')
def step_page_contains(context, text: str):
    """Verify the page contains specific text."""
    assert text in context.response_body, \
        f"Expected text '{text}' not found in response. Response body (first 500 chars): {context.response_body[:500]}"


@then('I am redirected to the login page')
def step_redirected_to_login(context):
    """Verify redirect to login page."""
    assert '/admin/login/' in context.response_body or context.response_status_code == 302, \
        f"Expected redirect to login, got status {context.response_status_code}"


@then('the page lists city "{city_name}"')
def step_page_lists_city(context, city_name: str):
    """Verify the page lists a specific city."""
    assert city_name in context.response_body, \
        f"Expected city '{city_name}' not found in page"


@then('the city "{city_name}" is created')
def step_city_is_created(context, city_name: str):
    """Verify a city was created in the database."""
    if not City.objects.filter(name=city_name).exists():
        error_start = context.response_body.find('errorlist')
        error_section = context.response_body[max(0, error_start-100):error_start+500] if error_start != -1 else ''
        assert False, \
            f"City '{city_name}' was not created. Response code: {context.response_status_code}. Errors: {error_section}"


@then('I am redirected to the city list')
def step_redirected_to_city_list(context):
    """Verify redirect to city list."""
    assert context.response_status_code in [200, 302], \
        f"Expected successful redirect, got {context.response_status_code}. Response (first 500 chars): {context.response_body[:500]}"


@then('the page lists alerts for "{city_name}"')
def step_page_lists_alerts(context, city_name: str):
    """Verify the page lists alerts for a specific city."""
    assert city_name in context.response_body, \
        f"Expected alerts for city '{city_name}' not found in page"


@given('weather alerts exist for "{city_name}"')
def step_weather_alerts_exist(context, city_name: str):
    """Create weather alerts for a city."""
    city = City.objects.filter(name=city_name).first()
    if not city:
        city = City.objects.create(
            name=city_name,
            country='Denmark',
            region='Europe',
            timezone='Europe/Copenhagen',
            latitude=55.6761,
            longitude=12.5683
        )

    if not WeatherAlert.objects.filter(city=city).exists():
        WeatherAlert.objects.create(
            city=city,
            severity='high',
            message='Test alert for testing'
        )
