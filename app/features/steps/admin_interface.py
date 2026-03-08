"""
Step definitions for Admin Content Management System feature.
"""
import json
import os
import re
import subprocess
import tempfile
import urllib.parse
from behave import given, when, then
from weather.models import City, WeatherAlert


@given('I am authenticated as admin via session')
def step_authenticate_admin_session(context):
    """Authenticate as admin using Django session cookies."""
    # Create temp file for cookies
    context.cookie_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt')
    context.cookie_file.close()

    # Get login page to obtain CSRF token
    cmd = [
        "curl",
        "--cookie-jar", context.cookie_file.name,
        "--silent",
        "--location",
        "http://localhost:8000/admin/login/"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    # Extract CSRF token from login page
    csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\'](.*?)["\']', result.stdout)
    if not csrf_match:
        raise ValueError("CSRF token not found in login page")
    csrf_token = csrf_match.group(1)

    # Submit login form
    login_data = {
        'username': 'admin',
        'password': 'admin',
        'csrfmiddlewaretoken': csrf_token,
        'next': '/admin/'
    }
    encoded_data = urllib.parse.urlencode(login_data)

    cmd = [
        "curl",
        "--cookie", context.cookie_file.name,
        "--cookie-jar", context.cookie_file.name,
        "--data", encoded_data,
        "--header", "Referer: http://localhost:8000/admin/login/",
        "--silent",
        "http://localhost:8000/admin/login/"
    ]
    subprocess.run(cmd, capture_output=True, text=True, check=True)

    # Store that we're authenticated as admin
    context.auth_type = 'admin'


@given('I am authenticated as regular user via session')
def step_authenticate_regular_user_session(context):
    """Authenticate as regular user using Django session cookies."""
    # First ensure regular user exists via API
    from django.contrib.auth import get_user_model
    User = get_user_model()

    if not User.objects.filter(username='regularuser').exists():
        User.objects.create_user(username='regularuser', password='password')

    # Create temp file for cookies
    context.cookie_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt')
    context.cookie_file.close()

    # Get login page to obtain CSRF token
    cmd = [
        "curl",
        "--cookie-jar", context.cookie_file.name,
        "--silent",
        "--location",
        "http://localhost:8000/admin/login/"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    # Extract CSRF token
    csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\'](.*?)["\']', result.stdout)
    if not csrf_match:
        raise ValueError("CSRF token not found in login page")
    csrf_token = csrf_match.group(1)

    # Submit login form with regular user credentials
    login_data = {
        'username': 'regularuser',
        'password': 'password',
        'csrfmiddlewaretoken': csrf_token,
        'next': '/admin/'
    }
    encoded_data = urllib.parse.urlencode(login_data)

    cmd = [
        "curl",
        "--cookie", context.cookie_file.name,
        "--cookie-jar", context.cookie_file.name,
        "--data", encoded_data,
        "--header", "Referer: http://localhost:8000/admin/login/",
        "--silent",
        "http://localhost:8000/admin/login/"
    ]
    subprocess.run(cmd, capture_output=True, text=True, check=True)

    # Store that we're authenticated as regular user
    context.auth_type = 'regular'


@given('cities exist in the database')
def step_cities_exist(context):
    """Create test cities in the database."""
    City.objects.create(
        name="Tokyo",
        country="Japan",
        region="Asia",
        timezone="Asia/Tokyo",
        latitude=35.6762,
        longitude=139.6503
    )
    City.objects.create(
        name="Delhi",
        country="India",
        region="Asia",
        timezone="Asia/Kolkata",
        latitude=28.7041,
        longitude=77.1025
    )


@given('weather alerts exist in the database')
def step_weather_alerts_exist(context):
    """Create test weather alerts in the database."""
    # First create a city
    city = City.objects.create(
        name="Shanghai",
        country="China",
        region="Asia",
        timezone="Asia/Shanghai",
        latitude=31.2304,
        longitude=121.4737
    )

    # Create weather alerts
    WeatherAlert.objects.create(
        city=city,
        severity='high',
        message='Heavy rain expected'
    )
    WeatherAlert.objects.create(
        city=city,
        severity='medium',
        message='Strong winds'
    )


@when('I navigate to "{url}"')
def step_navigate_to_url(context, url):
    """Navigate to a URL using session authentication."""
    cmd = [
        "curl",
        "--cookie", context.cookie_file.name,
        "--silent",
        "--write-out", "\nHTTP_STATUS_CODE:%{http_code}",
        f"http://localhost:8000{url}"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    # Extract status code
    status_match = re.search(r'HTTP_STATUS_CODE:(\d+)', result.stdout)
    if status_match:
        context.response_status_code = int(status_match.group(1))
        # Remove status code from response body
        context.response_body = re.sub(r'\nHTTP_STATUS_CODE:\d+$', '', result.stdout)
    else:
        context.response_status_code = 200
        context.response_body = result.stdout


@when('I submit the city creation form with:')
def step_submit_city_form(context):
    """Submit city creation form through admin interface."""
    # First GET the form page to extract CSRF token
    cmd = [
        "curl",
        "--cookie", context.cookie_file.name,
        "--silent",
        "http://localhost:8000/admin/weather/city/add/"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    # Extract CSRF token
    csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\'](.*?)["\']', result.stdout)
    if not csrf_match:
        raise ValueError("CSRF token not found in add city form")
    csrf_token = csrf_match.group(1)

    # Build form data from table
    form_data = {'csrfmiddlewaretoken': csrf_token}

    # First row contains headers in behave tables
    if context.table.headings:
        form_data[context.table.headings[0]] = context.table.headings[1]

    # Remaining rows
    for row in context.table:
        form_data[row.cells[0]] = row.cells[1]

    # Add required hidden fields for Django admin
    form_data['_save'] = 'Save'

    encoded_data = urllib.parse.urlencode(form_data)

    # Submit the form
    cmd = [
        "curl",
        "--cookie", context.cookie_file.name,
        "--cookie-jar", context.cookie_file.name,
        "--data", encoded_data,
        "--header", "Referer: http://localhost:8000/admin/weather/city/add/",
        "--silent",
        "--write-out", "\nHTTP_STATUS_CODE:%{http_code}",
        "http://localhost:8000/admin/weather/city/add/"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    # Extract status code
    status_match = re.search(r'HTTP_STATUS_CODE:(\d+)', result.stdout)
    if status_match:
        context.response_status_code = int(status_match.group(1))
        context.response_body = re.sub(r'\nHTTP_STATUS_CODE:\d+$', '', result.stdout)
    else:
        context.response_status_code = 200
        context.response_body = result.stdout

    # Store city name for later verification
    context.city_name = form_data.get('name')


@then('the page contains "{text}"')
def step_page_contains_text(context, text):
    """Verify page contains specific text."""
    assert text in context.response_body, \
        f"Expected text '{text}' not found in page"


@then('the page contains a list of cities')
def step_page_contains_city_list(context):
    """Verify admin page contains city list."""
    # Admin list page should contain table with cities
    assert 'Tokyo' in context.response_body or 'Delhi' in context.response_body, \
        "City list not found in admin page"


@then('the page contains weather alerts')
def step_page_contains_weather_alerts(context):
    """Verify admin page contains weather alerts."""
    assert 'Heavy rain expected' in context.response_body or 'Strong winds' in context.response_body, \
        "Weather alerts not found in admin page"


@then('a city "{city_name}" exists in the database')
def step_city_exists_in_database(context, city_name):
    """Verify city exists in database."""
    assert City.objects.filter(name=city_name).exists(), \
        f"City '{city_name}' not found in database"
