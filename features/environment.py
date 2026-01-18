"""
Behave environment setup for Django BDD testing.
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner
from django.test import Client
import json

# Add the app directory to sys.path so Django can find our project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.join(BASE_DIR, 'app')
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')

# Avoid errors when no database is configured yet
if not settings.configured:
    django.setup()


def before_all(context):
    """
    Setup before any scenarios run.
    """

    # Configure test settings
    TestRunner = get_runner(settings)
    context.test_runner = TestRunner(verbosity=0, interactive=False, keepdb=False)

    # Setup test environment and database only if not already setup
    try:
        context.test_runner.setup_test_environment()
        context.old_db = context.test_runner.setup_databases()
    except RuntimeError as e:
        if "setup_test_environment() was already called" in str(e):
            # Already setup by Django's test runner
            pass
        else:
            raise

    # Initialize HTTP client
    context.client = Client()

    # Store for access tokens and other state
    context.access_token = None
    context.refresh_token = None
    context.response = None
    context.response_data = None
    context.response_json = None
    context.users = {}
    context.cities = {}
    context.weather_data = {}
    context.last_weather = {}
    context.multiple_weather = {}
    context.full_weather = {}
    context.historical_weather = {}
    context.query_results = None
    context.graphql_response = None
    context.graphql_response_status = None
    context.graphql_response_data = None
    context.forecast_data = {}
    context.forecast_response = None
    context.forecast_response_status = None
    context.forecast_response_data = None

    # Create default test users
    create_test_users(context)

    print("Behave environment setup complete")


def after_all(context):
    """
    Cleanup after all scenarios.
    """
    if hasattr(context, 'test_runner') and hasattr(context, 'old_db'):
        try:
            context.test_runner.teardown_databases(context.old_db)
            context.test_runner.teardown_test_environment()
        except Exception as e:
            # Ignore cleanup errors
            pass


def before_scenario(context, scenario):
    """
    Setup before each scenario.
    """
    # Reset state for each scenario
    context.access_token = None
    context.refresh_token = None
    context.response = None
    context.response_data = None
    context.response_json = None
    context.last_weather = {}
    context.multiple_weather = {}
    context.full_weather = {}
    context.historical_weather = {}
    context.query_results = None
    context.graphql_response = None
    context.graphql_response_status = None
    context.graphql_response_data = None
    context.forecast_data = {}
    context.forecast_response = None
    context.forecast_response_status = None
    context.forecast_response_data = None

    # Ensure users exist for this scenario
    create_test_users(context)


def after_scenario(context, scenario):
    """
    Cleanup after each scenario.
    """
    # Clean up test data if needed
    pass


def create_test_users(context):
    """
    Create default test users for authentication scenarios.
    """
    from django.contrib.auth.models import User

    # Admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'password': 'admin',
            'email': 'admin@test.local',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin_user.set_password('admin')
        admin_user.save()
    context.users['admin'] = admin_user

    # Regular user
    regular_user, created = User.objects.get_or_create(
        username='user',
        defaults={
            'password': 'password',
            'email': 'user@test.local',
        }
    )
    if created:
        regular_user.set_password('password')
        regular_user.save()
    context.users['user'] = regular_user

    print(f"Test users created: {list(context.users.keys())}")
