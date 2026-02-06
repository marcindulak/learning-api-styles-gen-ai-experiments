from behave import given, then, when
from django.contrib.auth import get_user_model
from django.test import Client

from weather_service.models import City, WeatherRecord

User = get_user_model()


@given("an admin user is logged into the admin interface")
def step_admin_logged_into_admin(context):
    """Admin user is logged into the admin interface."""
    if not hasattr(context, "admin_user"):
        user = User.objects.create_user(username="admin", password="admin")
        user.is_staff = True
        user.is_superuser = True
        user.save()
        context.admin_user = user
        context.admin_username = "admin"
        context.admin_password = "admin"

    context.client = Client()
    logged_in = context.client.login(
        username=context.admin_username, password=context.admin_password
    )
    assert logged_in, "Admin user login failed"


@when('the admin user navigates to "{path}"')
def step_admin_navigates_to(context, path: str):
    """Admin navigates to specified path."""
    if not hasattr(context, "client"):
        context.client = Client()
    context.response = context.client.get(path)


@when("the admin user navigates to the admin interface")
def step_admin_navigates_to_admin(context):
    """Admin navigates to admin interface."""
    context.response = context.client.get("/admin/")


@when('logs in with username "{username}" and password "{password}"')
def step_logs_in_with_credentials(context, username: str, password: str):
    """User logs in with specified credentials."""
    logged_in = context.client.login(username=username, password=password)
    assert logged_in, f"Login failed for user {username}"
    context.response = context.client.get("/admin/")


@when("the admin navigates to the cities section")
def step_admin_navigates_to_cities(context):
    """Admin navigates to cities section in admin."""
    context.response = context.client.get("/admin/weather_service/city/")


@when("the admin navigates to the users section")
def step_admin_navigates_to_users(context):
    """Admin navigates to users section in admin."""
    context.response = context.client.get("/admin/auth/user/")


@when("the admin navigates to the weather records section")
def step_admin_navigates_to_weather_records(context):
    """Admin navigates to weather records section in admin."""
    context.response = context.client.get("/admin/weather_service/weatherrecord/")


@then("the admin user sees the Django admin dashboard")
def step_admin_sees_dashboard(context):
    """Verify admin sees the Django admin dashboard."""
    assert context.response.status_code == 200, f"Expected status 200, got {context.response.status_code}"
    assert b"Django administration" in context.response.content, "Django admin dashboard not found"


@then("the admin sees a list of cities")
def step_admin_sees_list_of_cities(context):
    """Verify admin sees list of cities."""
    assert context.response.status_code == 200, f"Expected status 200, got {context.response.status_code}"
    assert b"city" in context.response.content.lower(), "Cities section not found"


@then("the admin can add a new city")
def step_admin_can_add_city(context):
    """Verify admin can add a new city."""
    response = context.client.get("/admin/weather_service/city/add/")
    assert response.status_code == 200, f"Cannot access add city form, status {response.status_code}"


@then("the admin can edit existing cities")
def step_admin_can_edit_cities(context):
    """Verify admin can edit existing cities."""
    city = City.objects.first()
    if not city:
        city = City.objects.create(
            name="TestCity",
            country="Test",
            region="Test",
            timezone="UTC",
            latitude=0.0,
            longitude=0.0,
        )
    response = context.client.get(f"/admin/weather_service/city/{city.pk}/change/")
    assert response.status_code == 200, f"Cannot access edit city form, status {response.status_code}"


@then("the admin can delete cities")
def step_admin_can_delete_cities(context):
    """Verify admin can delete cities."""
    city = City.objects.first()
    if not city:
        city = City.objects.create(
            name="TestCityToDelete",
            country="Test",
            region="Test",
            timezone="UTC",
            latitude=0.0,
            longitude=0.0,
        )
    response = context.client.get(f"/admin/weather_service/city/{city.pk}/delete/")
    assert response.status_code == 200, f"Cannot access delete city form, status {response.status_code}"


@then("the admin sees a list of users")
def step_admin_sees_list_of_users(context):
    """Verify admin sees list of users."""
    assert context.response.status_code == 200, f"Expected status 200, got {context.response.status_code}"
    assert b"user" in context.response.content.lower(), "Users section not found"


@then("the admin can create new users")
def step_admin_can_create_users(context):
    """Verify admin can create new users."""
    response = context.client.get("/admin/auth/user/add/")
    assert response.status_code == 200, f"Cannot access add user form, status {response.status_code}"


@then("the admin can modify user permissions")
def step_admin_can_modify_permissions(context):
    """Verify admin can modify user permissions."""
    user = User.objects.first()
    if not user:
        user = User.objects.create_user(username="testuser", password="testpass")
    response = context.client.get(f"/admin/auth/user/{user.pk}/change/")
    assert response.status_code == 200, f"Cannot access edit user form, status {response.status_code}"
    assert b"permissions" in response.content.lower() or b"Permissions" in response.content


@then("the admin sees a list of weather records")
def step_admin_sees_list_of_weather_records(context):
    """Verify admin sees list of weather records."""
    assert context.response.status_code == 200, f"Expected status 200, got {context.response.status_code}"
    assert b"weather record" in context.response.content.lower(), "Weather records section not found"


@then("the admin can filter records by city")
def step_admin_can_filter_by_city(context):
    """Verify admin can filter records by city."""
    assert b"filter" in context.response.content.lower() or b"Filter" in context.response.content, "Filter options not found"


@then("the admin can view record details")
def step_admin_can_view_record_details(context):
    """Verify admin can view record details."""
    city = City.objects.first()
    if not city:
        city = City.objects.create(
            name="TestCity",
            country="Test",
            region="Test",
            timezone="UTC",
            latitude=0.0,
            longitude=0.0,
        )

    record = WeatherRecord.objects.first()
    if not record:
        record = WeatherRecord.objects.create(
            city=city,
            temperature=20.0,
            humidity=60,
            pressure=1013,
            wind_speed=10.0,
            precipitation=0.0,
        )

    response = context.client.get(f"/admin/weather_service/weatherrecord/{record.pk}/change/")
    assert response.status_code == 200, f"Cannot access weather record details, status {response.status_code}"
