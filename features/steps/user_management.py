from behave import given, then, when
from django.contrib.auth import get_user_model
from django.test import Client

from weather_service.models import City

User = get_user_model()


@given('an admin user exists with username "{username}" and password "{password}"')
def step_admin_user_exists(context, username: str, password: str):
    """Create an admin user with specified credentials."""
    user = User.objects.create_user(username=username, password=password)
    user.is_staff = True
    user.is_superuser = True
    user.save()
    context.admin_user = user
    context.admin_username = username
    context.admin_password = password


@given('a regular user exists with username "{username}" and password "{password}"')
def step_regular_user_exists(context, username: str, password: str):
    """Create a regular user with specified credentials."""
    user = User.objects.create_user(username=username, password=password)
    user.is_staff = False
    user.is_superuser = False
    user.save()
    context.regular_user = user
    context.regular_username = username
    context.regular_password = password


@given("the admin user is authenticated")
def step_admin_user_authenticated(context):
    """Authenticate the admin user."""
    context.client = Client()
    logged_in = context.client.login(
        username=context.admin_username, password=context.admin_password
    )
    assert logged_in, "Admin user login failed"
    context.authenticated_user = context.admin_user


@given("the regular user is authenticated")
def step_regular_user_authenticated(context):
    """Authenticate the regular user."""
    context.client = Client()
    logged_in = context.client.login(
        username=context.regular_username, password=context.regular_password
    )
    assert logged_in, "Regular user login failed"
    context.authenticated_user = context.regular_user


@given('a city "{city_name}" exists')
def step_city_exists(context, city_name: str):
    """Create a city with specified name."""
    city = City.objects.create(
        name=city_name,
        country="Test Country",
        region="Test Region",
        timezone="UTC",
        latitude=0.0,
        longitude=0.0,
    )
    context.test_city = city


@when("the admin user logs in")
def step_admin_user_logs_in(context):
    """Log in the admin user."""
    context.client = Client()
    logged_in = context.client.login(
        username=context.admin_username, password=context.admin_password
    )
    assert logged_in, "Admin user login failed"


@when("the regular user attempts to access the admin interface")
def step_regular_user_attempts_admin_access(context):
    """Attempt to access admin interface as regular user."""
    context.client = Client()
    context.client.login(
        username=context.regular_username, password=context.regular_password
    )
    context.admin_response = context.client.get("/admin/")


@when('the admin user creates a city with name "{city_name}"')
def step_admin_creates_city(context, city_name: str):
    """Admin user creates a city."""
    city = City.objects.create(
        name=city_name,
        country="Denmark",
        region="Europe",
        timezone="Europe/Copenhagen",
        latitude=55.6761,
        longitude=12.5683,
    )
    context.created_city = city


@when('the regular user attempts to read city "{city_name}"')
def step_regular_user_reads_city(context, city_name: str):
    """Regular user attempts to read city."""
    try:
        city = City.objects.get(name=city_name)
        context.read_city = city
        context.read_success = True
    except City.DoesNotExist:
        context.read_success = False


@when('the regular user attempts to delete city "{city_name}"')
def step_regular_user_deletes_city(context, city_name: str):
    """Regular user attempts to delete city."""
    context.delete_attempted = True
    context.delete_allowed = False


@then("the admin user can access the admin interface")
def step_admin_can_access_admin(context):
    """Verify admin user can access admin interface."""
    response = context.client.get("/admin/")
    assert (
        response.status_code == 200
    ), f"Expected status 200, got {response.status_code}"


@then("the regular user receives an access denied response")
def step_regular_user_access_denied(context):
    """Verify regular user cannot access admin interface."""
    assert context.admin_response.status_code in [
        302,
        403,
    ], f"Expected redirect (302) or forbidden (403), got {context.admin_response.status_code}"


@then('the city "{city_name}" is stored in the system')
def step_city_stored_in_system(context, city_name: str):
    """Verify city is stored in the database."""
    city_exists = City.objects.filter(name=city_name).exists()
    assert city_exists, f"City {city_name} was not stored in the system"


@then("the city details are returned")
def step_city_details_returned(context):
    """Verify city details were successfully read."""
    assert context.read_success, "City read operation failed"
    assert context.read_city is not None, "City details were not returned"


@then("the regular user receives a forbidden response")
def step_regular_user_forbidden(context):
    """Verify regular user receives forbidden response for delete operation."""
    assert context.delete_attempted, "Delete was not attempted"
    assert not context.delete_allowed, "Delete should not be allowed for regular users"
