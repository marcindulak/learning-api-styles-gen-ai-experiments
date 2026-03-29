# Weather Forecast Service Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Django-based Weather Forecast Service exposing REST, GraphQL, WebSocket, Atom, and Webhook APIs with PostgreSQL storage, Docker deployment, and behave-django tests.

**Architecture:** Single Django monolith using DRF for REST, Strawberry for GraphQL, Django Channels for WebSocket, and Django's built-in syndication for Atom feeds. The project lives at `./app/app/` (volume `./app` maps to `/app`; the ENTRYPOINT runs `app/scripts/startup.sh` from WORKDIR `/app`, resolving to `/app/app/scripts/startup.sh`).

**Tech Stack:** Python 3.13, Django 5.1, DRF + simplejwt, Strawberry GraphQL, Django Channels + Daphne, channels-redis, Open-Meteo API (free, no key), PostgreSQL 17, Redis, Docker Compose, behave-django, drf-spectacular.

---

## Infrastructure Overview

### Files Created / Modified

| Path | Action | Purpose |
|------|--------|---------|
| `requirements.txt` | Create | Python deps for Docker build |
| `compose.yaml` | Modify | Add redis service |
| `app/app/scripts/startup.sh` | Create | Migrate + start Daphne |
| `app/app/scripts/healthcheck.sh` | Create | HTTP health probe |
| `app/app/manage.py` | Create | Django entry point |
| `app/app/config/__init__.py` | Create | Package marker |
| `app/app/config/settings.py` | Create | Base Django settings |
| `app/app/config/postgres.py` | Create | PostgreSQL settings (extends base) |
| `app/app/config/asgi.py` | Create | ASGI + Channels routing |
| `app/app/config/urls.py` | Create | Root URL conf |
| `app/app/weather/__init__.py` | Create | Package marker |
| `app/app/weather/apps.py` | Create | AppConfig |
| `app/app/weather/models.py` | Create | City, WeatherRecord, WeatherForecast, WeatherAlert |
| `app/app/weather/admin.py` | Create | Django admin (CMS) |
| `app/app/weather/serializers.py` | Create | DRF serializers |
| `app/app/weather/views.py` | Create | REST ViewSets + webhook view |
| `app/app/weather/schema.py` | Create | Strawberry GraphQL schema |
| `app/app/weather/consumers.py` | Create | WebSocket alert consumer |
| `app/app/weather/feeds.py` | Create | Atom forecast feed |
| `app/app/weather/permissions.py` | Create | IsAdminOrReadOnly |
| `app/app/weather/services.py` | Create | Open-Meteo API client |
| `app/app/weather/migrations/` | Create | DB migrations |
| `app/app/features/cities.feature` | Create | Behave feature |
| `app/app/features/steps/steps.py` | Create | Behave step defs |
| `app/app/features/environment.py` | Create | Behave Django setup |
| `docs/api/openapi.yaml` | Create | OpenAPI 3.0 spec |
| `docs/api/asyncapi.yaml` | Create | AsyncAPI spec |

---

## Task 1: Add Redis to compose.yaml and create requirements.txt

**Files:**
- Modify: `compose.yaml`
- Create: `requirements.txt`

- [ ] **Step 1: Add redis service to compose.yaml**

Edit `compose.yaml` — add the redis service block after the postgres service, before the networks section:

```yaml
services:
  app:
    build:
      context: ./
      dockerfile: ./Dockerfile
    image: django/app
    container_name: django-app
    hostname: django-app
    networks:
      - django_internal
    ports:
      - 127.0.0.1:8000:8000
      - 127.0.0.1:8001:8001
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      - DEBUG=False
      - DJANGO_SETTINGS_MODULE=config.postgres
      - SECRET_KEY=${SECRET_KEY:-VKnroLzyyjvUk316fuyY2vO8jnrP6obbEjH75PGESQpf2Zwu2SJkGUme1cRj67Hz}
      - TLS_ENABLE=0
      - WEBHOOK_SECRET=${WEBHOOK_SECRET:-a0tObtQBvNhQjRSbPRZrIkXiooIH2ucIZJeESrRcIFyYOtSV8FKWrAri8djp3CQd}
      - POSTGRES_DB=weather_forecast_service
      - POSTGRES_HOST=postgres
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-postgres}
      - POSTGRES_USER=postgres
      - REDIS_HOST=redis
    volumes:
       - ./app:/app
       - ./docs:/app/docs

  postgres:
    image: postgres:17-alpine
    container_name: django-postgres
    hostname: django-postgres
    networks:
      - django_internal
    ports:
      - 127.0.0.1:5432:5432
    environment:
      - POSTGRES_DB=weather_forecast_service
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-postgres}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready"]
      interval: 5s
      timeout: 3s
      retries: 30

  redis:
    image: redis:7-alpine
    container_name: django-redis
    hostname: django-redis
    networks:
      - django_internal
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 30

networks:
  django_internal:
    name: django_internal
```

- [ ] **Step 2: Create requirements.txt at repo root**

Create `/vagrant/requirements.txt`:

```
Django==5.1.7
djangorestframework==3.15.2
djangorestframework-simplejwt==5.3.1
daphne==4.1.2
channels==4.1.0
channels-redis==4.2.0
strawberry-graphql[django]==0.234.1
drf-spectacular==0.27.2
feedgen==0.9.0
httpx==0.27.2
behave==1.2.6
behave-django==1.4.0
psycopg2-binary==2.9.9
redis==5.0.8
```

- [ ] **Step 3: Commit**

```bash
git add compose.yaml requirements.txt
git commit -m "feat: add redis service and Python requirements"
```

---

## Task 2: Scripts and Django project scaffold

**Files:**
- Create: `app/app/scripts/startup.sh`
- Create: `app/app/scripts/healthcheck.sh`
- Create: `app/app/manage.py`
- Create: `app/app/config/__init__.py`
- Create: `app/app/config/settings.py`
- Create: `app/app/config/postgres.py`
- Create: `app/app/config/asgi.py`
- Create: `app/app/config/urls.py`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p app/app/scripts app/app/config
touch app/app/config/__init__.py
```

- [ ] **Step 2: Create startup.sh**

Create `app/app/scripts/startup.sh`:

```sh
#!/bin/sh
set -e

APP_DIR="/app/app"

echo "==> Waiting for database..."
cd "$APP_DIR"
python manage.py wait_for_db 2>/dev/null || sleep 5

echo "==> Running migrations..."
python manage.py migrate --no-input

echo "==> Collecting static files..."
python manage.py collectstatic --no-input --clear

echo "==> Creating admin superuser (if not exists)..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Admin user created.')
else:
    print('Admin user already exists.')
"

echo "==> Starting Daphne ASGI server on port 8000..."
if [ "$TLS_ENABLE" = "1" ]; then
    exec daphne \
        --bind 0.0.0.0 \
        --port 8000 \
        --ssl-certificate "$APP_TLS_CERTS_DIR/cert.pem" \
        --ssl-private-key "$APP_TLS_PRICATE_DIR/key.pem" \
        config.asgi:application
else
    exec daphne \
        --bind 0.0.0.0 \
        --port 8000 \
        config.asgi:application
fi
```

Make it executable: `chmod +x app/app/scripts/startup.sh`

- [ ] **Step 3: Create healthcheck.sh**

Create `app/app/scripts/healthcheck.sh`:

```sh
#!/bin/sh
if [ "$TLS_ENABLE" = "1" ]; then
    curl --fail --silent --insecure https://localhost:8000/health/ || exit 1
else
    curl --fail --silent http://localhost:8000/health/ || exit 1
fi
```

Make it executable: `chmod +x app/app/scripts/healthcheck.sh`

- [ ] **Step 4: Create manage.py**

Create `app/app/manage.py`:

```python
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.postgres")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Create base settings**

Create `app/app/config/settings.py`:

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")

DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "channels",
    "strawberry_django",
    "drf_spectacular",
    "weather",
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

ASGI_APPLICATION = "config.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(os.environ.get("REDIS_HOST", "localhost"), 6379)],
        },
    },
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
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

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": [
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Weather Forecast Service API",
    "DESCRIPTION": "REST API for weather data across the world's 5 biggest cities.",
    "VERSION": "1.0.0",
}

WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "change-me")
```

- [ ] **Step 6: Create postgres settings**

Create `app/app/config/postgres.py`:

```python
from .settings import *  # noqa: F401, F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "weather_forecast_service"),
        "USER": os.environ.get("POSTGRES_USER", "postgres"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "postgres"),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}
```

Note: `os` is available via the wildcard import from settings.

- [ ] **Step 7: Create ASGI config**

Create `app/app/config/asgi.py`:

```python
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.postgres")
django.setup()

from weather.consumers import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        ),
    }
)
```

- [ ] **Step 8: Create root URL conf**

Create `app/app/config/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerUIView
import strawberry
import strawberry_django
from strawberry.django.views import GraphQLView
from weather.schema import schema
from weather.feeds import WeatherForecastFeed
from weather import views

urlpatterns = [
    path("admin/", admin.site.urls),
    # Health check
    path("health/", views.HealthView.as_view(), name="health"),
    # JWT
    path("api/jwt/obtain", TokenObtainPairView.as_view(), name="jwt-obtain"),
    path("api/jwt/refresh", TokenRefreshView.as_view(), name="jwt-refresh"),
    # REST API
    path("api/", include("weather.urls")),
    # GraphQL
    path("graphql/", GraphQLView.as_view(schema=schema)),
    # Atom feed
    path("feed/forecasts/", WeatherForecastFeed(), name="forecast-feed"),
    # OpenAPI
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerUIView.as_view(url_name="schema"), name="swagger-ui"),
]
```

- [ ] **Step 9: Commit**

```bash
git add app/
git commit -m "feat: add Django project scaffold, scripts, and config"
```

---

## Task 3: Domain models

**Files:**
- Create: `app/app/weather/__init__.py`
- Create: `app/app/weather/apps.py`
- Create: `app/app/weather/models.py`

- [ ] **Step 1: Create apps.py and __init__.py**

Create `app/app/weather/__init__.py` (empty).

Create `app/app/weather/apps.py`:

```python
from django.apps import AppConfig


class WeatherConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "weather"
```

- [ ] **Step 2: Create models.py**

Create `app/app/weather/models.py`:

```python
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class City(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    timezone = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "cities"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}, {self.country}"


class WeatherRecord(models.Model):
    """Actual historical weather data for a city."""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="weather_records")
    recorded_at = models.DateTimeField()
    temperature_celsius = models.FloatField()
    humidity_percent = models.FloatField()
    wind_speed_kmh = models.FloatField()
    precipitation_mm = models.FloatField(default=0.0)
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"{self.city.name} @ {self.recorded_at}: {self.temperature_celsius}°C"


class WeatherForecast(models.Model):
    """Up to 7-day weather forecast for a city."""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="forecasts")
    forecast_date = models.DateField()
    temperature_max_celsius = models.FloatField()
    temperature_min_celsius = models.FloatField()
    precipitation_mm = models.FloatField(default=0.0)
    wind_speed_kmh = models.FloatField()
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["forecast_date"]
        unique_together = [["city", "forecast_date"]]

    def __str__(self):
        return f"{self.city.name} forecast {self.forecast_date}"

    @classmethod
    def max_days(cls):
        return 7


class WeatherAlert(models.Model):
    """Weather alert broadcast via WebSocket."""
    SEVERITY_CHOICES = [
        ("info", "Info"),
        ("warning", "Warning"),
        ("severe", "Severe"),
        ("extreme", "Extreme"),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="alerts")
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    issued_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="alerts"
    )

    class Meta:
        ordering = ["-issued_at"]

    def __str__(self):
        return f"[{self.severity.upper()}] {self.city.name}: {self.title}"
```

- [ ] **Step 3: Create and run migration**

```bash
docker compose exec app bash -c "cd /app/app && python manage.py makemigrations weather"
docker compose exec app bash -c "cd /app/app && python manage.py migrate"
```

Expected: migration files created in `app/app/weather/migrations/`, tables created in PostgreSQL.

- [ ] **Step 4: Commit**

```bash
git add app/app/weather/
git commit -m "feat: add domain models (City, WeatherRecord, WeatherForecast, WeatherAlert)"
```

---

## Task 4: Django admin (CMS)

**Files:**
- Create: `app/app/weather/admin.py`

- [ ] **Step 1: Create admin.py**

Create `app/app/weather/admin.py`:

```python
from django.contrib import admin
from .models import City, WeatherRecord, WeatherForecast, WeatherAlert


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "region", "latitude", "longitude")
    search_fields = ("name", "country", "region")
    readonly_fields = ("uuid", "created_at", "updated_at")


@admin.register(WeatherRecord)
class WeatherRecordAdmin(admin.ModelAdmin):
    list_display = ("city", "recorded_at", "temperature_celsius", "humidity_percent", "wind_speed_kmh")
    list_filter = ("city",)
    search_fields = ("city__name",)
    readonly_fields = ("uuid", "created_at")
    ordering = ("-recorded_at",)


@admin.register(WeatherForecast)
class WeatherForecastAdmin(admin.ModelAdmin):
    list_display = ("city", "forecast_date", "temperature_max_celsius", "temperature_min_celsius")
    list_filter = ("city",)
    search_fields = ("city__name",)
    readonly_fields = ("uuid", "created_at", "updated_at")


@admin.register(WeatherAlert)
class WeatherAlertAdmin(admin.ModelAdmin):
    list_display = ("city", "severity", "title", "issued_at", "expires_at")
    list_filter = ("city", "severity")
    search_fields = ("title", "message", "city__name")
    readonly_fields = ("uuid",)
```

- [ ] **Step 2: Verify admin is accessible**

```bash
# Visit http://localhost:8000/admin/ in a browser
# Login: admin / admin
# Verify City, WeatherRecord, WeatherForecast, WeatherAlert are listed
```

- [ ] **Step 3: Commit**

```bash
git add app/app/weather/admin.py
git commit -m "feat: register models in Django admin (CMS)"
```

---

## Task 5: REST API — serializers, permissions, URLs, views

**Files:**
- Create: `app/app/weather/serializers.py`
- Create: `app/app/weather/permissions.py`
- Create: `app/app/weather/urls.py`
- Create: `app/app/weather/views.py`

- [ ] **Step 1: Create serializers.py**

Create `app/app/weather/serializers.py`:

```python
from rest_framework import serializers
from .models import City, WeatherRecord, WeatherForecast, WeatherAlert


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = [
            "uuid", "name", "country", "region",
            "timezone", "latitude", "longitude",
            "created_at", "updated_at",
        ]
        read_only_fields = ["uuid", "created_at", "updated_at"]


class WeatherRecordSerializer(serializers.ModelSerializer):
    city_uuid = serializers.UUIDField(source="city.uuid", read_only=True)
    city_name = serializers.CharField(source="city.name", read_only=True)

    class Meta:
        model = WeatherRecord
        fields = [
            "uuid", "city", "city_uuid", "city_name", "recorded_at",
            "temperature_celsius", "humidity_percent", "wind_speed_kmh",
            "precipitation_mm", "description", "created_at",
        ]
        read_only_fields = ["uuid", "city_uuid", "city_name", "created_at"]


class WeatherForecastSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source="city.name", read_only=True)

    class Meta:
        model = WeatherForecast
        fields = [
            "uuid", "city", "city_name", "forecast_date",
            "temperature_max_celsius", "temperature_min_celsius",
            "precipitation_mm", "wind_speed_kmh", "description",
            "created_at", "updated_at",
        ]
        read_only_fields = ["uuid", "city_name", "created_at", "updated_at"]

    def validate(self, data):
        from datetime import date, timedelta
        if "forecast_date" in data:
            max_date = date.today() + timedelta(days=WeatherForecast.max_days())
            if data["forecast_date"] > max_date:
                raise serializers.ValidationError(
                    {"forecast_date": f"Forecast cannot exceed {WeatherForecast.max_days()} days from today."}
                )
        return data


class WeatherAlertSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source="city.name", read_only=True)

    class Meta:
        model = WeatherAlert
        fields = [
            "uuid", "city", "city_name", "severity", "title", "message",
            "issued_at", "expires_at", "created_by",
        ]
        read_only_fields = ["uuid", "city_name", "created_by"]
```

- [ ] **Step 2: Create permissions.py**

Create `app/app/weather/permissions.py`:

```python
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """Admin users have full CRUD; regular users and anonymous have read-only."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
```

- [ ] **Step 3: Create views.py**

Create `app/app/weather/views.py`:

```python
import hashlib
import hmac
import json

from django.conf import settings
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import City, WeatherRecord, WeatherForecast, WeatherAlert
from .permissions import IsAdminOrReadOnly
from .serializers import (
    CitySerializer, WeatherRecordSerializer,
    WeatherForecastSerializer, WeatherAlertSerializer,
)


class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"status": "ok"})


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "country", "region"]
    ordering_fields = ["name", "country"]
    lookup_field = "uuid"

    def get_queryset(self):
        qs = super().get_queryset()
        search_name = self.request.query_params.get("search_name")
        if search_name:
            qs = qs.filter(name__icontains=search_name)
        return qs

    @action(detail=True, methods=["get"], url_path="forecasts")
    def forecasts(self, request, uuid=None):
        city = self.get_object()
        forecasts = city.forecasts.all()
        serializer = WeatherForecastSerializer(forecasts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="records")
    def records(self, request, uuid=None):
        city = self.get_object()
        records = city.weather_records.all()
        serializer = WeatherRecordSerializer(records, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="import-forecast")
    def import_forecast(self, request, uuid=None):
        """Import 7-day forecast from Open-Meteo for this city."""
        from .services import fetch_and_store_forecast
        city = self.get_object()
        try:
            count = fetch_and_store_forecast(city)
            return Response({"imported": count})
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)


class WeatherRecordViewSet(viewsets.ModelViewSet):
    queryset = WeatherRecord.objects.select_related("city").all()
    serializer_class = WeatherRecordSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["city__name"]
    ordering_fields = ["recorded_at", "temperature_celsius"]
    lookup_field = "uuid"


class WeatherForecastViewSet(viewsets.ModelViewSet):
    queryset = WeatherForecast.objects.select_related("city").all()
    serializer_class = WeatherForecastSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["city__name"]
    ordering_fields = ["forecast_date"]
    lookup_field = "uuid"


class WeatherAlertViewSet(viewsets.ModelViewSet):
    queryset = WeatherAlert.objects.select_related("city", "created_by").all()
    serializer_class = WeatherAlertSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["city__name", "title"]
    ordering_fields = ["issued_at", "severity"]
    lookup_field = "uuid"

    def perform_create(self, serializer):
        alert = serializer.save(created_by=self.request.user)
        # Broadcast via WebSocket
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"alerts_{alert.city.uuid}",
            {
                "type": "alert.message",
                "uuid": str(alert.uuid),
                "city": alert.city.name,
                "severity": alert.severity,
                "title": alert.title,
                "message": alert.message,
                "issued_at": alert.issued_at.isoformat(),
            },
        )


@method_decorator(csrf_exempt, name="dispatch")
class GitHubWebhookView(View):
    """Receive GitHub webhook events and log them."""

    def post(self, request):
        signature = request.headers.get("X-Hub-Signature-256", "")
        secret = settings.WEBHOOK_SECRET.encode()
        digest = "sha256=" + hmac.new(secret, request.body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, digest):
            return JsonResponse({"error": "Invalid signature"}, status=403)

        event = request.headers.get("X-GitHub-Event", "unknown")
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        # Log the event (extensible: trigger CI, update docs, etc.)
        print(f"GitHub webhook received: event={event}, action={payload.get('action', 'n/a')}")
        return JsonResponse({"received": True, "event": event})
```

- [ ] **Step 4: Create urls.py**

Create `app/app/weather/urls.py`:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"cities", views.CityViewSet, basename="city")
router.register(r"records", views.WeatherRecordViewSet, basename="weatherrecord")
router.register(r"forecasts", views.WeatherForecastViewSet, basename="weatherforecast")
router.register(r"alerts", views.WeatherAlertViewSet, basename="weatheralert")

urlpatterns = [
    path("", include(router.urls)),
    path("webhooks/github/", views.GitHubWebhookView.as_view(), name="github-webhook"),
]
```

- [ ] **Step 5: Write failing test**

Create `app/app/features/cities.feature`:

```gherkin
Feature: Cities API
  As a user
  I want to manage cities
  So that I can access weather data

  Scenario: List cities returns empty list initially
    Given I am an unauthenticated user
    When I GET /api/cities
    Then the response status is 200
    And the response contains a results list

  Scenario: Admin can create a city
    Given I am authenticated as admin
    When I POST /api/cities with Tokyo data
    Then the response status is 201
    And the response contains the city name Tokyo

  Scenario: Regular user cannot create a city
    Given I am authenticated as a regular user
    When I POST /api/cities with Delhi data
    Then the response status is 403
```

- [ ] **Step 6: Create behave environment.py**

Create `app/app/features/environment.py`:

```python
from behave_django import auto_use_db  # noqa: F401


def before_all(context):
    context.base_url = "http://localhost:8000"
```

- [ ] **Step 7: Create step definitions**

Create `app/app/features/steps/steps.py`:

```python
from behave import given, when, then
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@given("I am an unauthenticated user")
def step_unauthenticated(context):
    context.client = APIClient()


@given("I am authenticated as admin")
def step_admin(context):
    context.client = APIClient()
    user, _ = User.objects.get_or_create(
        username="test_admin",
        defaults={"is_staff": True, "is_superuser": True},
    )
    user.set_password("password")
    user.save()
    response = context.client.post(
        "/api/jwt/obtain",
        {"username": "test_admin", "password": "password"},
        format="json",
    )
    token = response.data["access"]
    context.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


@given("I am authenticated as a regular user")
def step_regular_user(context):
    context.client = APIClient()
    user, _ = User.objects.get_or_create(
        username="test_user",
        defaults={"is_staff": False},
    )
    user.set_password("password")
    user.save()
    response = context.client.post(
        "/api/jwt/obtain",
        {"username": "test_user", "password": "password"},
        format="json",
    )
    token = response.data["access"]
    context.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


@when("I GET /api/cities")
def step_get_cities(context):
    context.response = context.client.get("/api/cities")


@when("I POST /api/cities with Tokyo data")
def step_post_tokyo(context):
    context.response = context.client.post(
        "/api/cities",
        {
            "name": "Tokyo",
            "country": "Japan",
            "region": "Asia",
            "timezone": "Asia/Tokyo",
            "latitude": 35.6762,
            "longitude": 139.6503,
        },
        format="json",
    )


@when("I POST /api/cities with Delhi data")
def step_post_delhi(context):
    context.response = context.client.post(
        "/api/cities",
        {
            "name": "Delhi",
            "country": "India",
            "region": "Asia",
            "timezone": "Asia/Kolkata",
            "latitude": 28.6139,
            "longitude": 77.2090,
        },
        format="json",
    )


@then("the response status is {status_code:d}")
def step_status_code(context, status_code):
    assert context.response.status_code == status_code, (
        f"Expected {status_code}, got {context.response.status_code}: {context.response.data}"
    )


@then("the response contains a results list")
def step_results_list(context):
    assert "results" in context.response.data, f"No 'results' key in {context.response.data}"


@then("the response contains the city name {name}")
def step_city_name(context, name):
    assert context.response.data.get("name") == name, (
        f"Expected name={name}, got {context.response.data}"
    )
```

- [ ] **Step 8: Run tests to verify they fail**

```bash
docker compose exec app bash -c "cd /app/app && python manage.py behave --no-input 2>&1 | head -40"
```

Expected: ModuleNotFoundError or ImportError since `weather` app is not fully wired.

- [ ] **Step 9: Build and start services**

```bash
docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)
docker compose up --detach --wait
```

Expected: All three services start healthy.

- [ ] **Step 10: Run tests to verify they pass**

```bash
docker compose exec app bash -c "cd /app/app && python manage.py behave --no-input"
```

Expected: All 3 scenarios pass.

- [ ] **Step 11: Commit**

```bash
git add app/app/weather/ app/app/features/ app/app/config/urls.py
git commit -m "feat: add REST API for cities, records, forecasts, alerts + behave tests"
```

---

## Task 6: GraphQL API

**Files:**
- Create: `app/app/weather/schema.py`

- [ ] **Step 1: Create schema.py**

Create `app/app/weather/schema.py`:

```python
from typing import List, Optional
import strawberry
from strawberry.types import Info
from .models import City, WeatherRecord, WeatherForecast, WeatherAlert


@strawberry.django.type(City)
class CityType:
    uuid: strawberry.ID
    name: str
    country: str
    region: str
    timezone: str
    latitude: float
    longitude: float


@strawberry.django.type(WeatherRecord)
class WeatherRecordType:
    uuid: strawberry.ID
    recorded_at: str
    temperature_celsius: float
    humidity_percent: float
    wind_speed_kmh: float
    precipitation_mm: float
    description: str


@strawberry.django.type(WeatherForecast)
class WeatherForecastType:
    uuid: strawberry.ID
    forecast_date: str
    temperature_max_celsius: float
    temperature_min_celsius: float
    precipitation_mm: float
    wind_speed_kmh: float
    description: str


@strawberry.type
class Query:
    @strawberry.field
    def cities(self) -> List[CityType]:
        return City.objects.all()

    @strawberry.field
    def city(self, uuid: strawberry.ID) -> Optional[CityType]:
        try:
            return City.objects.get(uuid=uuid)
        except City.DoesNotExist:
            return None

    @strawberry.field
    def weather_records(self, city_uuid: strawberry.ID) -> List[WeatherRecordType]:
        return WeatherRecord.objects.filter(city__uuid=city_uuid)

    @strawberry.field
    def forecasts(self, city_uuid: strawberry.ID) -> List[WeatherForecastType]:
        return WeatherForecast.objects.filter(city__uuid=city_uuid)


schema = strawberry.Schema(query=Query)
```

- [ ] **Step 2: Add GraphQL feature test**

Add to `app/app/features/cities.feature`:

```gherkin
  Scenario: GraphQL query returns cities
    Given I am an unauthenticated user
    When I query GraphQL for all cities
    Then the GraphQL response contains a cities list
```

- [ ] **Step 3: Add GraphQL step definitions**

Append to `app/app/features/steps/steps.py`:

```python
@when("I query GraphQL for all cities")
def step_graphql_cities(context):
    context.response = context.client.post(
        "/graphql/",
        {"query": "{ cities { uuid name country } }"},
        format="json",
    )


@then("the GraphQL response contains a cities list")
def step_graphql_cities_list(context):
    data = context.response.json()
    assert "data" in data, f"No 'data' key in {data}"
    assert "cities" in data["data"], f"No 'cities' key in {data['data']}"
    assert isinstance(data["data"]["cities"], list)
```

- [ ] **Step 4: Run tests**

```bash
docker compose exec app bash -c "cd /app/app && python manage.py behave --no-input"
```

Expected: All scenarios pass including GraphQL scenario.

- [ ] **Step 5: Commit**

```bash
git add app/app/weather/schema.py app/app/features/
git commit -m "feat: add GraphQL API with Strawberry"
```

---

## Task 7: Atom feed

**Files:**
- Create: `app/app/weather/feeds.py`

- [ ] **Step 1: Create feeds.py**

Create `app/app/weather/feeds.py`:

```python
from django.contrib.syndication.views import Feed
from django.utils import timezone
from .models import WeatherForecast


class WeatherForecastFeed(Feed):
    title = "Weather Forecast Service - 7-Day Forecasts"
    link = "/feed/forecasts/"
    description = "7-day weather forecasts for the world's biggest cities."

    def items(self):
        return WeatherForecast.objects.select_related("city").order_by("-updated_at")[:50]

    def item_title(self, item):
        return f"{item.city.name}: {item.forecast_date} — {item.description or 'Forecast'}"

    def item_description(self, item):
        return (
            f"Date: {item.forecast_date}\n"
            f"High: {item.temperature_max_celsius}°C  Low: {item.temperature_min_celsius}°C\n"
            f"Wind: {item.wind_speed_kmh} km/h  Precipitation: {item.precipitation_mm} mm"
        )

    def item_pubdate(self, item):
        return item.updated_at

    def item_link(self, item):
        return f"/api/forecasts/{item.uuid}"
```

- [ ] **Step 2: Verify feed is accessible**

```bash
docker compose exec app bash -c "curl --silent http://localhost:8000/feed/forecasts/ | head -20"
```

Expected: Atom XML output with `<feed>` root element.

- [ ] **Step 3: Commit**

```bash
git add app/app/weather/feeds.py
git commit -m "feat: add Atom feed for weather forecasts"
```

---

## Task 8: WebSocket alerts consumer

**Files:**
- Create: `app/app/weather/consumers.py`

- [ ] **Step 1: Create consumers.py**

Create `app/app/weather/consumers.py`:

```python
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class WeatherAlertConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for live weather alerts per city."""

    async def connect(self):
        self.city_uuid = self.scope["url_route"]["kwargs"]["city_uuid"]
        self.group_name = f"alerts_{self.city_uuid}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({
            "type": "connected",
            "city_uuid": self.city_uuid,
            "message": f"Subscribed to alerts for city {self.city_uuid}",
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        # Clients can send ping to keep connection alive
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return
        if data.get("type") == "ping":
            await self.send(text_data=json.dumps({"type": "pong"}))

    async def alert_message(self, event):
        """Receive alert from channel layer and forward to WebSocket client."""
        await self.send(text_data=json.dumps({
            "type": "alert",
            "uuid": event["uuid"],
            "city": event["city"],
            "severity": event["severity"],
            "title": event["title"],
            "message": event["message"],
            "issued_at": event["issued_at"],
        }))


websocket_urlpatterns = [
    # ws://localhost:8000/ws/alerts/<city-uuid>/
    __import__("django.urls", fromlist=["re_path"]).re_path(
        r"ws/alerts/(?P<city_uuid>[0-9a-f-]+)/$",
        WeatherAlertConsumer.as_asgi(),
    ),
]
```

- [ ] **Step 2: Test WebSocket connection**

```bash
# node-ws is installed in the container (node-ws package)
docker compose exec app bash -c \
  "echo '{\"type\":\"ping\"}' | wscat --connect ws://localhost:8000/ws/alerts/00000000-0000-0000-0000-000000000000/ --no-color 2>&1 | head -5" \
  || echo "wscat not available, check with manual test"
```

Expected: Connection accepted, `{"type":"connected",...}` message received.

- [ ] **Step 3: Commit**

```bash
git add app/app/weather/consumers.py app/app/config/asgi.py
git commit -m "feat: add WebSocket consumer for real-time weather alerts"
```

---

## Task 9: Open-Meteo weather integration

**Files:**
- Create: `app/app/weather/services.py`

- [ ] **Step 1: Create services.py**

Create `app/app/weather/services.py`:

```python
"""Open-Meteo API integration (https://open-meteo.com/ — free, no API key required)."""
import httpx
from datetime import date, timedelta
from django.utils.timezone import make_aware
from datetime import datetime

from .models import City, WeatherForecast, WeatherRecord

OPEN_METEO_BASE = "https://api.open-meteo.com/v1"


def fetch_and_store_forecast(city: City) -> int:
    """Fetch 7-day forecast from Open-Meteo and save to database. Returns count of upserted rows."""
    url = f"{OPEN_METEO_BASE}/forecast"
    params = {
        "latitude": city.latitude,
        "longitude": city.longitude,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max,weathercode",
        "forecast_days": 7,
        "timezone": city.timezone,
    }
    with httpx.Client(timeout=10) as client:
        response = client.get(url, params=params)
        response.raise_for_status()

    data = response.json()["daily"]
    count = 0
    for i, forecast_date_str in enumerate(data["time"]):
        forecast_date = date.fromisoformat(forecast_date_str)
        WeatherForecast.objects.update_or_create(
            city=city,
            forecast_date=forecast_date,
            defaults={
                "temperature_max_celsius": data["temperature_2m_max"][i],
                "temperature_min_celsius": data["temperature_2m_min"][i],
                "precipitation_mm": data["precipitation_sum"][i] or 0.0,
                "wind_speed_kmh": data["windspeed_10m_max"][i] or 0.0,
                "description": _wmo_code_to_description(data["weathercode"][i]),
            },
        )
        count += 1
    return count


def fetch_and_store_historical(city: City, days_back: int = 7) -> int:
    """Fetch recent historical weather from Open-Meteo and save as WeatherRecords."""
    end_date = date.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=days_back - 1)
    url = f"{OPEN_METEO_BASE}/archive"
    params = {
        "latitude": city.latitude,
        "longitude": city.longitude,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "hourly": "temperature_2m,relativehumidity_2m,windspeed_10m,precipitation",
        "timezone": city.timezone,
    }
    with httpx.Client(timeout=30) as client:
        response = client.get(url, params=params)
        response.raise_for_status()

    data = response.json()["hourly"]
    count = 0
    for i, ts in enumerate(data["time"]):
        recorded_at = make_aware(datetime.fromisoformat(ts))
        WeatherRecord.objects.get_or_create(
            city=city,
            recorded_at=recorded_at,
            defaults={
                "temperature_celsius": data["temperature_2m"][i] or 0.0,
                "humidity_percent": data["relativehumidity_2m"][i] or 0.0,
                "wind_speed_kmh": data["windspeed_10m"][i] or 0.0,
                "precipitation_mm": data["precipitation"][i] or 0.0,
            },
        )
        count += 1
    return count


# WMO weather code mapping (https://open-meteo.com/en/docs#weathervariables)
_WMO_DESCRIPTIONS = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
}


def _wmo_code_to_description(code: int) -> str:
    return _WMO_DESCRIPTIONS.get(code, f"Code {code}")
```

- [ ] **Step 2: Seed the 5 biggest cities via management command**

Create `app/app/weather/management/__init__.py` (empty).
Create `app/app/weather/management/commands/__init__.py` (empty).

Create `app/app/weather/management/commands/seed_cities.py`:

```python
from django.core.management.base import BaseCommand
from weather.models import City
from weather.services import fetch_and_store_forecast

CITIES = [
    {"name": "Tokyo", "country": "Japan", "region": "Asia", "timezone": "Asia/Tokyo", "latitude": 35.6762, "longitude": 139.6503},
    {"name": "Delhi", "country": "India", "region": "Asia", "timezone": "Asia/Kolkata", "latitude": 28.6139, "longitude": 77.2090},
    {"name": "Shanghai", "country": "China", "region": "Asia", "timezone": "Asia/Shanghai", "latitude": 31.2304, "longitude": 121.4737},
    {"name": "Dhaka", "country": "Bangladesh", "region": "Asia", "timezone": "Asia/Dhaka", "latitude": 23.8103, "longitude": 90.4125},
    {"name": "São Paulo", "country": "Brazil", "region": "Americas", "timezone": "America/Sao_Paulo", "latitude": -23.5505, "longitude": -46.6333},
]


class Command(BaseCommand):
    help = "Seed the database with the 5 biggest cities and their 7-day forecasts"

    def handle(self, *args, **options):
        for city_data in CITIES:
            city, created = City.objects.get_or_create(
                name=city_data["name"],
                defaults=city_data,
            )
            action = "Created" if created else "Skipped"
            self.stdout.write(f"{action}: {city}")
            if created:
                try:
                    count = fetch_and_store_forecast(city)
                    self.stdout.write(f"  Imported {count} forecast days for {city.name}")
                except Exception as exc:
                    self.stderr.write(f"  Failed to import forecast for {city.name}: {exc}")
        self.stdout.write(self.style.SUCCESS("Done."))
```

- [ ] **Step 3: Run seed command**

```bash
docker compose exec app bash -c "cd /app/app && python manage.py seed_cities"
```

Expected output:
```
Created: Tokyo, Japan
  Imported 7 forecast days for Tokyo
Created: Delhi, India
  ...
Done.
```

- [ ] **Step 4: Commit**

```bash
git add app/app/weather/services.py app/app/weather/management/
git commit -m "feat: integrate Open-Meteo API and seed 5 biggest cities"
```

---

## Task 10: API documentation (OpenAPI + AsyncAPI)

**Files:**
- Create: `docs/api/asyncapi.yaml`

The OpenAPI spec is auto-generated by drf-spectacular at `/api/schema/`.

- [ ] **Step 1: Export OpenAPI spec**

```bash
mkdir -p docs/api
docker compose exec app bash -c "cd /app/app && python manage.py spectacular --file /app/docs/api/openapi.yaml --validate"
```

Expected: `docs/api/openapi.yaml` is created with the full spec.

- [ ] **Step 2: Create AsyncAPI spec for WebSocket**

Create `docs/api/asyncapi.yaml`:

```yaml
asyncapi: "2.6.0"
info:
  title: Weather Forecast Service - WebSocket API
  version: "1.0.0"
  description: Real-time weather alerts via WebSocket

servers:
  local:
    url: ws://localhost:8000
    protocol: ws

channels:
  /ws/alerts/{cityUuid}/:
    description: Subscribe to weather alerts for a specific city
    parameters:
      cityUuid:
        description: UUID of the city to subscribe to
        schema:
          type: string
          format: uuid
    subscribe:
      summary: Receive weather alerts
      message:
        oneOf:
          - $ref: "#/components/messages/Connected"
          - $ref: "#/components/messages/Alert"
          - $ref: "#/components/messages/Pong"
    publish:
      summary: Send ping to keep connection alive
      message:
        $ref: "#/components/messages/Ping"

components:
  messages:
    Connected:
      payload:
        type: object
        properties:
          type:
            type: string
            const: connected
          city_uuid:
            type: string
          message:
            type: string
    Alert:
      payload:
        type: object
        properties:
          type:
            type: string
            const: alert
          uuid:
            type: string
          city:
            type: string
          severity:
            type: string
            enum: [info, warning, severe, extreme]
          title:
            type: string
          message:
            type: string
          issued_at:
            type: string
            format: date-time
    Ping:
      payload:
        type: object
        properties:
          type:
            type: string
            const: ping
    Pong:
      payload:
        type: object
        properties:
          type:
            type: string
            const: pong
```

- [ ] **Step 3: Commit**

```bash
git add docs/api/
git commit -m "docs: add OpenAPI and AsyncAPI specifications"
```

---

## Task 11: End-to-end tests (curl)

**Files:** No new files — run curl commands to validate the full stack.

- [ ] **Step 1: Obtain JWT access token**

```bash
CREDENTIALS_PAYLOAD='{"username":"admin","password":"admin"}'
ACCESS_TOKEN=$(docker compose exec app bash -c \
  "curl \
  --data '$CREDENTIALS_PAYLOAD' \
  --header 'Content-Type: application/json' \
  --request 'POST' \
  --silent 'http://localhost:8000/api/jwt/obtain' | \
  jq --raw-output '.access'")
echo "Token: $ACCESS_TOKEN"
```

Expected: JWT token printed to stdout.

- [ ] **Step 2: Create a city**

```bash
CREATE_CITY_PAYLOAD='{"name":"Copenhagen","country":"Denmark","region":"Europe","timezone":"Europe/Copenhagen","latitude":55.6761,"longitude":12.5683}'
docker compose exec app bash -c \
  "curl \
  --data '$CREATE_CITY_PAYLOAD' \
  --header 'Authorization: Bearer $ACCESS_TOKEN' \
  --header 'Content-Type: application/json' \
  --request 'POST' \
  --silent \
  'http://localhost:8000/api/cities' | jq"
```

Expected: JSON with `"name": "Copenhagen"` and a `uuid` field.

- [ ] **Step 3: Search and retrieve the city**

```bash
CITY_UUID=$(docker compose exec app bash -c \
  "curl --request 'GET' --silent 'http://localhost:8000/api/cities?search_name=Copenhagen' | \
  jq --raw-output '.results[0].uuid'")
docker compose exec app bash -c \
  "curl --request 'GET' --silent 'http://localhost:8000/api/cities/$CITY_UUID' | jq"
```

Expected: City JSON with correct UUID.

- [ ] **Step 4: Test Atom feed**

```bash
docker compose exec app bash -c "curl --silent http://localhost:8000/feed/forecasts/ | head -20"
```

Expected: Atom XML feed.

- [ ] **Step 5: Test GraphQL**

```bash
docker compose exec app bash -c \
  "curl --silent --header 'Content-Type: application/json' \
  --data '{\"query\":\"{cities{uuid name country}}\"}' \
  http://localhost:8000/graphql/ | jq"
```

Expected: `{"data": {"cities": [...]}}`.

- [ ] **Step 6: Test health endpoint**

```bash
docker compose exec app bash -c "curl --silent http://localhost:8000/health/ | jq"
```

Expected: `{"status": "ok"}`.

- [ ] **Step 7: Commit**

```bash
git add .
git commit -m "feat: complete Weather Forecast Service implementation"
```

---

## Spec Coverage Checklist

| Requirement | Task(s) |
|-------------|---------|
| REST API for weather indicators | Task 5 (CityViewSet, WeatherRecordViewSet, WeatherForecastViewSet) |
| GraphQL API | Task 6 |
| GitHub webhooks | Task 5 (GitHubWebhookView) |
| Atom feed | Task 7 |
| WebSocket alerts | Task 8 |
| Historical data | Task 9 (fetch_and_store_historical) |
| Admin CMS | Task 4 |
| 3rd party weather API | Task 9 (Open-Meteo) |
| 5 biggest cities | Task 9 (seed_cities command) |
| 7-day forecast limit | Task 3 (WeatherForecast.max_days), Task 5 (serializer validation) |
| Admin + regular user | Task 5 (IsAdminOrReadOnly) |
| Docker containers | Task 1 (compose.yaml) + Task 2 (scripts) |
| TLS | Task 2 (startup.sh TLS_ENABLE branch) |
| Monolith | Single Django app |
| behave-django tests | Task 5 (features/), Task 6 (GraphQL scenario) |
| OpenAPI spec | Task 10 (drf-spectacular) |
| AsyncAPI spec | Task 10 (docs/api/asyncapi.yaml) |
| GitHub Codespaces compatible | Docker-based, port-forwarded setup |
