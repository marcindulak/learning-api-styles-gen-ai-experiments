# Project: Weather Forecast Service

**Last Updated:** 2026-02-21

## Overview

Educational Django monolith demonstrating multiple web API patterns in a single application. Exposes weather data for the 5 biggest cities through REST, GraphQL, WebSocket, Atom feeds, and GitHub webhooks.

## Technology Stack

- **Language:** Python 3.13
- **Framework:** Django 5.1
- **Database:** PostgreSQL 17
- **APIs:** Django REST Framework, strawberry-django (GraphQL), Django Channels (WebSocket)
- **HTTP Server:** Gunicorn (port 8000)
- **WebSocket Server:** Daphne (port 8001)
- **Authentication:** djangorestframework-simplejwt (JWT)
- **Documentation:** drf-spectacular (OpenAPI), AsyncAPI
- **Testing:** behave (BDD), pytest, Django test framework
- **Package Manager:** uv (MANDATORY - never use pip)
- **Containerization:** Docker, Docker Compose

## Directory Structure

```
weather-forecast-service/
├── app/
│   ├── weather/              # Django app
│   │   ├── models.py         # Domain models (City, WeatherRecord, Forecast, WeatherAlert, WebhookEvent)
│   │   ├── views.py          # REST API viewsets
│   │   ├── serializers.py    # DRF serializers
│   │   ├── schema.py         # GraphQL schema (strawberry)
│   │   ├── consumers.py      # WebSocket consumers
│   │   ├── feeds.py          # Atom feed classes
│   │   ├── webhooks.py       # GitHub webhook handler
│   │   ├── urls.py           # URL routing
│   │   ├── signals.py        # Django signals (WebSocket broadcasts)
│   │   ├── permissions.py    # DRF permission classes
│   │   └── management/       # Management commands
│   ├── config/               # Project settings
│   │   ├── settings.py       # Base Django settings
│   │   ├── postgres.py       # PostgreSQL-specific settings
│   │   ├── urls.py           # Root URL configuration
│   │   └── asgi.py           # ASGI config (Channels)
│   ├── scripts/
│   │   ├── startup.sh        # Container startup
│   │   ├── healthcheck.sh    # Health checks
│   │   └── generate_certs.sh # TLS certificate generator
│   └── features/             # BDD scenarios
├── tests/                    # pytest tests
├── docs/plans/               # Implementation plans
├── Dockerfile
├── compose.yaml
└── requirements.txt
```

## Key Files

- **Configuration:** `app/config/settings.py`, `app/config/postgres.py`, `compose.yaml`
- **Entry Points:** `app/manage.py`, `app/config/asgi.py`
- **Domain Models:** `app/weather/models.py`
- **Tests:** `tests/test_*.py`, `app/features/*.feature`
- **API Schema:** `app/weather/schema.py` (GraphQL), `app/weather/views.py` (REST)

## Development Commands

**Setup:**
```bash
docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)
docker compose up --detach --wait
```

**Testing:**
```bash
# BDD tests (MUST run in Docker)
docker compose exec app python manage.py behave --no-input

# All tests
docker compose exec app python manage.py test

# Specific test modules
docker compose exec app python manage.py test tests.test_weather_rest -v 2
```

**Database:**
```bash
docker compose exec app python manage.py makemigrations
docker compose exec app python manage.py migrate
docker compose exec app python manage.py seed_data  # Seed 5 cities
```

**Development:**
```bash
docker compose down      # Stop services
docker compose ps        # Check status
docker compose logs app  # View logs
```

## Architecture Notes

**Monolithic Design:** All API patterns integrated in a single Django project.

**API Endpoints:**
- REST: `/api/cities/`, `/api/weather-records/`, `/api/forecasts/`
- GraphQL: `/api/graphql/` (queries & mutations)
- WebSocket: `ws://localhost:8001/ws/alerts/`
- Atom Feeds: `/api/feeds/forecasts/`
- Webhooks: `/api/webhooks/github/`
- Docs: `/api/docs/` (Swagger), `/api/docs/redoc/`

**Authentication:** JWT tokens via `/api/jwt/obtain` and `/api/jwt/refresh`

**Users:** Two pre-created users - `admin:admin` (full CRUD) and `regularuser:regularuser` (read-only)

**Domain Models:** All use UUID primary keys. Forecast limited to 7 days (enforced at model level).

**WebSocket Broadcasting:** Django signals trigger real-time alerts via in-memory channel layer.

**Testing Strategy:** BDD scenarios with behave, unit tests with pytest, integration tests with Django test framework.

## Docker Workflow

**All tests MUST run in Docker containers.** The project uses Docker Compose for orchestration with PostgreSQL and Django services.

**Container Ports:**
- 8000: HTTP (Gunicorn)
- 8001: WebSocket (Daphne)
- 5432: PostgreSQL (internal only)

**Permission Management:** Docker commands allowed in `.claude/settings.json` - both user-level and project-level configurations updated.

## Common Patterns

**UUID Primary Keys:** All domain models use UUID for database portability.

**Signal-Based Real-Time:** WeatherAlert creation triggers Django signal → broadcasts to WebSocket consumers.

**Model Validation:** Forecast model enforces 7-day limit in `clean()` method.

**Permission Classes:** `IsAdminOrReadOnly` enforces role-based access (admin = CRUD, regular = read-only).

**Error Handling:** Views raise `ValidationError` for invalid input with structured error messages. Webhooks log exceptions and return generic 500 errors.
