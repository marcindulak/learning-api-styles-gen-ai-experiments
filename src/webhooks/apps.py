"""Application configuration for the webhooks Django app."""

from __future__ import annotations

from django.apps import AppConfig


class WebhooksConfig(AppConfig):
    """Registers the webhooks app with Django's app registry."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "webhooks"
