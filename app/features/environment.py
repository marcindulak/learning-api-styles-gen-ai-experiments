"""Behave environment configuration."""
import os

import django
from behave.runner import Context

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.postgres')


def before_all(context: Context) -> None:
    """Run before all tests."""
    django.setup()


def before_scenario(context: Context, scenario) -> None:
    """Run before each scenario."""
    from django.contrib.auth import get_user_model
    from weather.models import City, WeatherRecord, WeatherForecast, WeatherAlert, WebhookEvent

    User = get_user_model()
    User.objects.all().delete()
    City.objects.all().delete()
    WeatherRecord.objects.all().delete()
    WeatherForecast.objects.all().delete()
    WeatherAlert.objects.all().delete()
    WebhookEvent.objects.all().delete()


def after_scenario(context: Context, scenario) -> None:
    """Run after each scenario."""
    pass
