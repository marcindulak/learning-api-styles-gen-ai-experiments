"""Behave environment configuration."""

import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.wfs.settings')
django.setup()


def before_scenario(context, scenario):
    """Clean up the database before each scenario."""
    from src.weather.models import City
    City.objects.all().delete()
