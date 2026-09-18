from behave import given, then, when
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from weather.models import City, WeatherRecord

CITY_DEFAULTS = {
    "country": "Testland",
    "region": "Testregion",
    "timezone": "UTC",
    "latitude": 0.0,
    "longitude": 0.0,
}

CMS_SECTIONS = ("Cities", "Weather records")


def _client_for(context, username):
    context.clients = getattr(context, "clients", {})
    return context.clients.setdefault(username, Client())


def _post_as(context, username, path, payload):
    context.last_response = _client_for(context, username).post(path, payload, follow=True)


def _post_login(context, username, password, next_path):
    _post_as(context, username, reverse("admin:login"), {
        "username": username, "password": password, "next": next_path,
    })


@given('an admin user "{username}" with password "{password}"')
def step_given_admin_user(context, username, password):
    User.objects.create_user(username, password=password, is_staff=True, is_superuser=True)


@given('a regular user "{username}" with password "{password}"')
def step_given_regular_user(context, username, password):
    User.objects.create_user(username, password=password, is_staff=False)


@when('"{username}" logs into "{path}" with password "{password}"')
@when('"{username}" attempts to log into "{path}" with password "{password}"')
def step_when_logs_into(context, username, path, password):
    _post_login(context, username, password, path)


@given('"{username}" is logged into "{path}"')
def step_given_logged_in(context, username, path):
    # A precondition setup, not itself exercising the login view, so it uses
    # Django's force_login test helper rather than posting credentials.
    user = User.objects.get(username=username)
    _client_for(context, username).force_login(user)


@then("the login succeeds")
def step_then_login_succeeds(context):
    assert context.last_response.status_code == 200
    assert context.last_response.redirect_chain, "expected a redirect to the admin dashboard"


@then("the login is rejected")
def step_then_login_rejected(context):
    assert context.last_response.status_code == 200
    assert not context.last_response.redirect_chain, "expected no redirect (login rejected)"


@then('the CMS dashboard lists the "{section1}" and "{section2}" sections')
def step_then_dashboard_lists_sections(context, section1, section2):
    body = context.last_response.content.decode()
    assert section1 in body
    assert section2 in body


@then('"{username}" is not shown the CMS dashboard')
def step_then_dashboard_not_shown(context, username):
    body = context.last_response.content.decode()
    assert not any(section in body for section in CMS_SECTIONS)


@when('"{username}" creates a city named "{name}" via the CMS')
def step_when_creates_city(context, username, name):
    _post_as(context, username, reverse("admin:weather_city_add"), {"name": name, **CITY_DEFAULTS})


@then('a city named "{name}" exists in the service')
def step_then_city_exists(context, name):
    assert City.objects.filter(name=name).exists()


@given('the city "{name}" exists')
def step_given_city_exists(context, name):
    City.objects.get_or_create(name=name, defaults=CITY_DEFAULTS)


@when('"{username}" creates a weather record for "{city_name}" with temperature {temperature} via the CMS')
def step_when_creates_weather_record(context, username, city_name, temperature):
    city = City.objects.get(name=city_name)
    _post_as(context, username, reverse("admin:weather_weatherrecord_add"), {
        "city": str(city.pk), "temperature": temperature,
    })


@then('a weather record for "{city_name}" with temperature {temperature} exists in the service')
def step_then_weather_record_exists(context, city_name, temperature):
    assert WeatherRecord.objects.filter(city__name=city_name, temperature=float(temperature)).exists()
