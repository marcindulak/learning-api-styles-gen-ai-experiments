"""Default Django settings for the Weather Forecast Service.

Designed to run out of the box for development and tests using SQLite, with
production-friendly knobs (SECRET_KEY, DEBUG) read from environment variables
so deployment can override them without editing the file.
"""

from __future__ import annotations

import os
from pathlib import Path


# src/config/settings.py -> src/config/ -> src/
BASE_DIR = Path(__file__).resolve().parent.parent

# In production this MUST be set via the environment. The fallback exists only
# so `manage.py` can run for local development and tests; it is not a secret.
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "insecure-development-secret-key-do-not-use-in-production",
)

DEBUG = os.environ.get("DEBUG", "False").lower() in {"1", "true", "yes"}

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    # behave_django registers the `manage.py behave` command prescribed by
    # REQUIREMENTS.md ("docker compose exec app python manage.py behave").
    "behave_django",
    "rest_framework",
    # graphene_django registers the GraphQLView used by the /graphql endpoint
    # introduced in FR-002 and reads the schema location from the GRAPHENE
    # setting at the bottom of this file.
    "graphene_django",
    # drf_spectacular generates the OpenAPI 3 schema served at /api/schema
    # and powers the Swagger UI mounted at /api/docs (NFR-005).
    "drf_spectacular",
    "cities",
    "webhooks",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

# DRF configuration:
#
# * Page-number pagination so list responses include the
#   ``count``/``results`` envelope FR-009 asserts.
# * Authentication classes order matters: JWTAuthentication runs first so a
#   ``Authorization: Bearer ...`` header is recognised, then
#   SessionAuthentication so the Django admin session and the FR-009
#   admin-POST scenario continue to work without a JWT.
# Shared secret used to verify HMAC SHA-256 signatures on incoming GitHub
# webhook deliveries (FR-003). An empty default disables the endpoint in
# practice because no signature can match; production deployments must
# configure a real secret via the environment.
GITHUB_WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "")

# Base URL of the third-party weather provider (FR-008). When empty the
# /api/cities/<name>/weather/current endpoint returns the FR-001
# placeholder reading; when set, the endpoint fetches live data from this
# URL and wraps it with a ``source.provider`` envelope. Tests override
# this value through ``override_settings``.
WEATHER_PROVIDER_URL = os.environ.get("WEATHER_PROVIDER_URL", "")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 100,
    # drf-spectacular ships its own AutoSchema; setting it here means the
    # schema served at /api/schema reflects every viewset/view in the project
    # without per-view opt-in.
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Weather Forecast Service API",
    "VERSION": "1.0.0",
    # The OpenAPI schema is served as YAML by default; Swagger UI fetches it
    # from /api/schema, so the URL name has to match the route registered in
    # config/urls.py.
    "SCHEMA_PATH_PREFIX": "/api/",
}

GRAPHENE = {
    "SCHEMA": "cities.schema.schema",
}
