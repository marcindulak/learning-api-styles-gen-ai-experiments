import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ["SECRET_KEY"]

WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]

# NFR-004/REQUIREMENTS.md's own end-to-end curl walkthrough authenticates as
# this admin user; seeded at startup (see weather.services.seed_admin_user)
# so the walkthrough works against a fresh checkout with no manual step.
ADMIN_USERNAME = os.environ["ADMIN_USERNAME"]
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]

DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "channels",
    "behave_django",
    "rest_framework",
    "drf_spectacular",
    "strawberry_django",
    "weather",
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
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# FR-004: a single process serves every connection (matches NFR-003's
# single-container/single-unit deployment), so the in-memory channel layer
# is sufficient -- no cross-process pub/sub is needed and no broker (e.g.
# Redis) is introduced.
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# FR-010: JWTAuthentication is the only authentication class in use so far
# (no endpoint uses session- or basic-auth login), and DEFAULT_PERMISSION_CLASSES
# is left at DRF's own default (AllowAny) since most existing endpoints are
# intentionally public reads; the few endpoints that need restriction opt in
# via their own permission_classes instead.
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # NFR-004: REQUIREMENTS.md's own curl walkthrough reads the created
    # city's UUID from a `.results[0]` wrapper, which DRF only produces once
    # a pagination class is configured; PageNumberPagination's own PAGE_SIZE
    # default is None (pagination class enabled but inactive), so PAGE_SIZE
    # must also be set explicitly.
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

# NFR-005: only TITLE is required by drf-spectacular; every other setting is
# left at its default per CLAUDE.md's "use default settings as much as
# possible" guidance.
SPECTACULAR_SETTINGS = {
    "TITLE": "Weather Forecast Service API",
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ["POSTGRES_HOST"],
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
