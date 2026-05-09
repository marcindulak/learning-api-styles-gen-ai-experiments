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
    "cities",
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
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 100,
}
