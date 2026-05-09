"""Application configuration for the cities Django app."""

from __future__ import annotations

from django.apps import AppConfig


class CitiesConfig(AppConfig):
    """Registers the cities app with Django's app registry."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "cities"
