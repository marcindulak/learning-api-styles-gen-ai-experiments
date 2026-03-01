"""Weather app configuration."""
from django.apps import AppConfig


class WeatherConfig(AppConfig):
    """Weather app configuration."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'weather'
