# Weather Forecast Service Implementation Plan

Created: 2026-02-20
Status: VERIFIED
Approved: Yes
Iterations: 1
Worktree: No

> **✅ VERIFICATION PHASE COMPLETE** - Docker tests executed successfully
>
> **Docker Infrastructure Status:** ✅ All services running
> - Python 3.13, all dependencies installed + PostgreSQL 17 healthy
> - Gunicorn (HTTP/8000) + Daphne (WebSocket/8001) running
> - Database migrations + admin/regular users created
> - BDD tests executed: `docker compose exec app python manage.py behave --no-input`
>
> **Code Review & Verification (Phase A) Complete.** Review agents found 20 issues (7 must_fix, 10 should_fix, 3 suggestions).
> **FIXED (11 of 7 must_fix + 4 of 10 should_fix):**
> - ✅ Signals registration (apps.py ready() method)
> - ✅ WebSocket consumer URL kwargs scope fix
> - ✅ E2E test script GET auth headers
> - ✅ TLS cert filename alignment (server.crt/server.key)
> - ✅ Dockerfile typo (APP_TLS_PRIVATE_DIR)
> - ✅ GraphQL test library (strawberry-compatible)
> - ✅ GraphQL context.request.user verification test
> - ✅ Invalid date format error handling (ValidationError)
> - ✅ GraphQL IntegrityError message safety
> - ✅ Webhook error message safety + logging
> **IN PROGRESS:** Webhook rate limiting, WebSocket E2E test, BDD auth, GraphQL pagination
> **SKIPPED (reasonable trade-offs):** Webhook regex patterns, seed_data tests, broad exception catches in feature code

> **Status Lifecycle:** PENDING -> COMPLETE -> VERIFIED
> **Iterations:** Tracks implement->verify cycles (incremented by verify phase)
>
> - PENDING: Initial state, awaiting implementation
> - COMPLETE: All tasks implemented
> - VERIFIED: All checks passed
>
> **Approval Gate:** Implementation CANNOT proceed until `Approved: Yes`
> **Worktree:** Set at plan creation (from dispatcher). `Yes` uses git worktree isolation; `No` works directly on current branch (default)

## Summary

**Goal:** Build an educational Weather Forecast Service (WFS) Django application that demonstrates multiple web API patterns (REST, GraphQL, WebSocket, Atom feed, GitHub webhooks) in a single monolithic project, serving mock weather data for the 5 biggest cities in the world with 7-day forecast limits.

**Architecture:** Django monolith with DRF for REST, strawberry-django for GraphQL, Django Channels (in-memory layer) for WebSocket alerts, Django syndication for Atom feeds, and a custom webhook receiver for GitHub integration. PostgreSQL for persistence. Two user roles (admin/regular) with DRF-based permission classes. All containerized via Docker.

**Tech Stack:** Python 3.13, Django, Django REST Framework, strawberry-django (GraphQL), Django Channels, djangorestframework-simplejwt (JWT), drf-spectacular (OpenAPI docs), PostgreSQL 17, Docker

## Scope

### In Scope

- Django project skeleton with proper settings, scripts, and Docker integration
- Domain models: City, WeatherRecord, Forecast, WeatherAlert, WebhookEvent
- Django admin CMS for weather data management
- JWT authentication with admin/regular user roles
- REST API: CRUD for cities, weather records, forecasts (7-day limit), historical data
- GraphQL API: queries and mutations via strawberry-django
- Atom feed: weather forecast feed per city
- WebSocket: real-time weather alert notifications via Django Channels (in-memory layer)
- GitHub webhook receiver with HMAC signature validation
- TLS support (self-signed certs, configurable via TLS_ENABLE)
- API documentation: OpenAPI (drf-spectacular) for REST, AsyncAPI spec for WebSocket
- Mock/seed data for 5 cities: Tokyo, Delhi, Shanghai, Sao Paulo, Mexico City
- BDD tests with django-behave and curl-based E2E test scripts

### Out of Scope

- Real 3rd party weather API integration (using mock/seed data only)
- Redis (using in-memory channel layer for WebSocket)
- Frontend/UI (API-only service, Django admin serves as CMS)
- Production deployment (educational/local environment only)
- Rate limiting, API versioning
- GitHub Codespaces configuration files

## Prerequisites

- Docker and Docker Compose installed (provided by Vagrantfile)
- Existing `Dockerfile` and `compose.yaml` at project root
- PostgreSQL 17 container (defined in compose.yaml)

## Context for Implementer

- **Patterns to follow:** This is a greenfield Django project. Follow standard Django conventions: apps in their own directories, models/views/serializers in separate modules within each app.
- **Conventions:** UUID primary keys for all domain models. API prefix `/api/`. Settings split into base and postgres modules (`config.settings` and `config.postgres`). `DJANGO_SETTINGS_MODULE=config.postgres` in compose.yaml.
- **Key files the Dockerfile expects:**
  - `requirements.txt` at project root (used during `docker compose build`)
  - `scripts/startup.sh` — container entrypoint (runs migrations, collectstatic, starts server)
  - `scripts/healthcheck.sh` — container health check
- **Docker volume mounts:** `./app:/app` maps host Django code to container. `./docs:/app/docs` maps docs.
- **Gotchas:**
  - The Dockerfile uses `WORKDIR app` (becomes `/app`), then `COPY . ${WORKDIR}` which copies to `/app/app/`. The `scripts/` and `requirements.txt` at project root get copied to `/app/app/` during build. The volume mount `./app:/app` overrides at runtime, so the Django code in `./app/` is what runs.
  - The Dockerfile references scripts as `${WORKDIR}/scripts/startup.sh` which resolves to `app/scripts/startup.sh` -> `/app/app/scripts/`. To make this work at runtime with the volume mount, scripts must be at `./app/scripts/` on the host.
  - The `redis` service is referenced in compose.yaml `depends_on` but not defined. Task 1 must remove this reference since we're using in-memory channels.
- **Domain context:**
  - Weather indicators: temperature, feels_like, humidity, wind_speed, wind_direction, pressure, precipitation, uv_index, visibility, cloud_cover, description
  - 5 cities by population: Tokyo (Japan), Delhi (India), Shanghai (China), Sao Paulo (Brazil), Mexico City (Mexico)
  - Forecasts limited to 7 days ahead
  - Two users: admin (full CRUD), regular (read-only)

## Runtime Environment

- **Start command:** `docker compose up --detach --wait`
- **Build command:** `docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)`
- **Ports:** 8000 (HTTP/HTTPS), 8001 (WebSocket)
- **Health check:** `docker compose exec app app/scripts/healthcheck.sh` or `curl http://localhost:8000/api/`
- **Restart procedure:** `docker compose restart app`
- **BDD tests:** `docker compose exec app python manage.py behave --no-input`

## Progress Tracking

**MANDATORY: Update this checklist as tasks complete. Change `[ ]` to `[x]`.**

- [x] Task 1: Django project skeleton and Docker infrastructure
- [x] Task 2: Domain models and database migrations
- [x] Task 3: Django admin CMS and seed data
- [x] Task 4: JWT authentication and permissions
- [x] Task 5: REST API — Cities
- [x] Task 6: REST API — Weather data and forecasts
- [x] Task 7: GraphQL API
- [x] Task 8: Atom feed for weather forecasts
- [x] Task 9: WebSocket weather alerts
- [x] Task 10: GitHub webhooks
- [x] Task 11: TLS configuration and API documentation
- [x] Task 12: BDD tests and E2E test scripts

**Total Tasks:** 12 | **Completed:** 12 | **Remaining:** 0

## Implementation Tasks

### Task 1: Django Project Skeleton and Docker Infrastructure

**Objective:** Create the Django project structure, configuration, startup scripts, requirements file, and fix Docker compose to remove the undefined redis dependency. The project should start up successfully in Docker with an empty database.

**Dependencies:** None

**Files:**

- Create: `app/manage.py`
- Create: `app/config/__init__.py`
- Create: `app/config/settings.py` (base settings)
- Create: `app/config/postgres.py` (PostgreSQL settings, imports from base)
- Create: `app/config/urls.py` (root URL config)
- Create: `app/config/wsgi.py`
- Create: `app/config/asgi.py` (ASGI for Channels)
- Create: `app/weather/__init__.py`
- Create: `app/weather/apps.py`
- Create: `app/scripts/startup.sh` (run migrations, create superuser, start gunicorn)
- Create: `app/scripts/healthcheck.sh`
- Create: `requirements.txt`
- Modify: `compose.yaml` (remove redis from depends_on)

**Key Decisions / Notes:**

- `DJANGO_SETTINGS_MODULE=config.postgres` is set in compose.yaml. The `config.postgres` module imports everything from `config.settings` and overrides DB settings.
- Base settings include: INSTALLED_APPS (django defaults + rest_framework, strawberry, channels, behave_django), MIDDLEWARE, AUTH, static files, REST_FRAMEWORK defaults.
- `startup.sh`: wait for postgres using `until pg_isready` loop with timeout, run `migrate`, create admin superuser if not exists, create regular user (user/user) for testing, run `collectstatic --noinput`, start gunicorn (port 8000) and daphne (port 8001) as background processes. Use `wait -n` to exit if either process dies. Store PIDs and trap SIGTERM to forward to both processes.
- `healthcheck.sh`: check BOTH ports — `curl localhost:8000` (HTTP) AND `nc -zv localhost 8001` (WebSocket). Use `http` or `https` scheme based on `TLS_ENABLE` env var. Include initial 2-second delay tolerance for cert generation.
- requirements.txt: Pin versions for compatibility — `Django>=5.0,<5.2`, `strawberry-graphql-django` (pin to known Django 5.x compatible version), `behave-django` (verify compatibility). All deps: Django, djangorestframework, djangorestframework-simplejwt, strawberry-graphql-django, channels, drf-spectacular, behave-django, gunicorn, daphne, psycopg2-binary.
- The `weather` app will be registered in INSTALLED_APPS but has no models yet (just `apps.py`).
- compose.yaml: remove `redis` from `depends_on`, add `condition: service_healthy` to postgres dependency to avoid startup race.
- Dockerfile path resolution: `${WORKDIR}/scripts/startup.sh` resolves to `app/scripts/startup.sh` -> `/app/app/scripts/` at build time. With volume mount `./app:/app`, scripts at host `./app/scripts/` are accessible at `/app/scripts/` in the container. Verify this path resolution explicitly after startup.

**Definition of Done:**

- [ ] **CRITICAL:** compose.yaml `depends_on` contains ONLY `postgres: { condition: service_healthy }` — redis reference REMOVED (critical fix)
- [ ] **CRITICAL:** `docker compose config --quiet` validates compose file succeeds (catches redis reference error)
- [ ] `docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)` succeeds
- [ ] `docker compose up --detach --wait` starts containers successfully
- [ ] `docker compose exec app python manage.py check` passes with no errors
- [ ] `docker compose exec app python manage.py showmigrations` shows Django migrations ready
- [ ] `docker compose exec app python manage.py behave --help` runs without import errors (django-behave compatibility verified)
- [ ] Admin superuser (admin/admin) auto-created: `docker compose exec app python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(username='admin').exists())"` outputs True
- [ ] Regular user (user/user) auto-created: `docker compose exec app python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(username='user').exists())"` outputs True
- [ ] **CRITICAL - Path verification:** `docker compose exec app ls /app/scripts/startup.sh /app/scripts/healthcheck.sh` — both scripts exist at /app/scripts/ (not /app/app/scripts/)
- [ ] **CRITICAL - Path executable:** `docker compose exec app test -x /app/scripts/startup.sh && test -x /app/scripts/healthcheck.sh` — both are executable
- [ ] **CRITICAL - Port 8000 accessible:** `curl --write-out "%{http_code}" --silent --output /dev/null http://localhost:8000/` returns HTTP code (200, 404, etc., NOT connection error)
- [ ] **CRITICAL - Port 8001 accessible:** `nc -zv localhost 8001` succeeds (WebSocket port listening)
- [ ] **CRITICAL - Both servers running:** `docker compose exec app ps aux | grep -E "(gunicorn|daphne)"` shows both processes active

**Verify:**

- `docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)` — build succeeds
- `docker compose up --detach --wait` — containers start and are healthy
- `docker compose exec app python manage.py check` — Django system check passes
- `curl --write-out "%{http_code}" --silent --output /dev/null http://localhost:8000/` — returns HTTP status code (not connection error)
- `docker compose exec app ls /app/scripts/startup.sh /app/scripts/healthcheck.sh` — both scripts exist at expected paths

---

### Task 2: Domain Models and Database Migrations

**Objective:** Create the core domain models (City, WeatherRecord, Forecast, WeatherAlert, WebhookEvent) with UUID primary keys, appropriate fields for weather indicators, and generate database migrations.

**Dependencies:** Task 1

**Files:**

- Create: `app/weather/models.py`
- Create: `app/weather/migrations/0001_initial.py` (auto-generated)

**Key Decisions / Notes:**

- **City model:** uuid (UUIDField, PK), name, country, region, timezone, latitude (DecimalField), longitude (DecimalField), created_at, updated_at. Unique constraint on (name, country).
- **WeatherRecord model:** uuid (PK), city (FK), recorded_at (DateTimeField), temperature, feels_like, humidity, wind_speed, wind_direction, pressure, precipitation, uv_index, visibility, cloud_cover (all DecimalField), description (CharField). Index on (city, recorded_at).
- **Forecast model:** uuid (PK), city (FK), forecast_date (DateField), temperature_high, temperature_low, humidity, wind_speed, precipitation_probability, description, created_at. Unique constraint on (city, forecast_date). Validation: forecast_date <= today + 7 days.
- **WeatherAlert model:** uuid (PK), city (FK), alert_type (choices: storm, heat, cold, flood, wind), severity (choices: advisory, watch, warning), title, description, issued_at, expires_at, is_active (BooleanField).
- **WebhookEvent model:** uuid (PK), event_type, payload (JSONField), received_at, processed (BooleanField).

**Definition of Done:**

- [ ] All 5 models defined with correct field types and constraints
- [ ] `python manage.py makemigrations weather` generates migration without errors
- [ ] `python manage.py migrate` applies all migrations successfully
- [ ] Model `__str__` methods return readable representations
- [ ] City uniqueness constraint works (duplicate name+country raises IntegrityError)

**Verify:**

- `docker compose exec app python manage.py makemigrations weather --check` — no new migrations needed
- `docker compose exec app python manage.py migrate --run-syncdb` — all applied
- `docker compose exec app python manage.py shell -c "from weather.models import City; print(City._meta.get_fields())"` — fields exist

---

### Task 3: Django Admin CMS and Seed Data

**Objective:** Register all domain models in Django admin with useful list displays, search, and filters. Create a management command to seed the database with the 5 cities and mock weather data (records + 7-day forecasts).

**Dependencies:** Task 2

**Files:**

- Create: `app/weather/admin.py`
- Create: `app/weather/management/__init__.py`
- Create: `app/weather/management/commands/__init__.py`
- Create: `app/weather/management/commands/seed_data.py`

**Key Decisions / Notes:**

- Admin registrations: CityAdmin (list: name, country, region), WeatherRecordAdmin (list: city, recorded_at, temperature; filters: city), ForecastAdmin (list: city, forecast_date, temp high/low; filters: city), WeatherAlertAdmin (list: city, alert_type, severity, is_active), WebhookEventAdmin (list: event_type, received_at, processed).
- `seed_data` command: creates 5 cities with coordinates and timezone, generates 30 days of historical WeatherRecord data per city (realistic temperature ranges per city), generates 7-day forecasts per city, creates 1-2 sample active weather alerts.
- Temperature ranges per city: Tokyo (5-35C), Delhi (10-45C), Shanghai (2-38C), Sao Paulo (15-35C), Mexico City (5-30C).
- Command is idempotent (skips if cities already exist).

**Definition of Done:**

- [ ] Django admin at `/admin/` shows all 5 models with list/search/filter
- [ ] `python manage.py seed_data` populates 5 cities, ~150 weather records, 35 forecasts, and sample alerts
- [ ] Running `seed_data` twice does not create duplicates
- [ ] Admin login with admin/admin works and shows populated data

**Verify:**

- `docker compose exec app python manage.py seed_data` — completes without error
- `docker compose exec app python manage.py shell -c "from weather.models import City; print(City.objects.count())"` — outputs 5
- `docker compose exec app bash -c "curl --silent http://localhost:8000/admin/ | grep -o 'Log in'"` — admin login page accessible

---

### Task 4: JWT Authentication and Permissions

**Objective:** Configure djangorestframework-simplejwt for JWT token authentication, create token obtain/refresh endpoints at `/api/jwt/obtain` and `/api/jwt/refresh`, and implement custom permission classes for admin (full CRUD) and regular users (read-only).

**Dependencies:** Task 1

**Files:**

- Create: `app/weather/permissions.py`
- Modify: `app/config/settings.py` (add REST_FRAMEWORK and SIMPLE_JWT settings)
- Modify: `app/config/urls.py` (add JWT URL patterns)

**Key Decisions / Notes:**

- REST_FRAMEWORK default authentication: JWTAuthentication. Default permission: IsAuthenticated for write operations.
- Custom permission class `IsAdminOrReadOnly`: admin user has full access, regular user can only use safe methods (GET, HEAD, OPTIONS).
- JWT endpoints: `/api/jwt/obtain` (TokenObtainPairView), `/api/jwt/refresh` (TokenRefreshView).
- Access token lifetime: 60 minutes. Refresh token lifetime: 1 day.
- `startup.sh` should also create a regular user (user/user) for testing read-only access.

**Definition of Done:**

- [ ] POST to `/api/jwt/obtain` with admin credentials returns access+refresh tokens
- [ ] POST to `/api/jwt/obtain` with regular user credentials returns tokens
- [ ] POST to `/api/jwt/refresh` with refresh token returns new access token
- [ ] Authenticated admin can perform POST/PUT/DELETE on protected endpoints
- [ ] Authenticated regular user gets 403 on POST/PUT/DELETE, 200 on GET
- [ ] Unauthenticated requests to protected endpoints get 401
- [ ] Regular user (username=user, password=user) is auto-created by startup script: `docker compose exec app python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(username='user').exists())"` outputs True

**Verify:**

- `docker compose exec app bash -c "curl --silent --data '{\"username\":\"admin\",\"password\":\"admin\"}' --header 'Content-Type: application/json' --request POST http://localhost:8000/api/jwt/obtain | jq '.access'"` — returns a JWT token string

---

### Task 5: REST API — Cities

**Objective:** Create a DRF viewset for City CRUD operations with UUID-based lookups, search filtering by name, and pagination. Admin users get full CRUD; regular users get read-only access.

**Dependencies:** Task 2, Task 4

**Files:**

- Create: `app/weather/serializers.py`
- Create: `app/weather/views.py`
- Create: `app/weather/urls.py`
- Modify: `app/config/urls.py` (include weather.urls)

**Key Decisions / Notes:**

- CitySerializer: all fields except created_at/updated_at for write; all fields for read.
- CityViewSet: ModelViewSet, lookup_field='uuid', permission_classes=[IsAdminOrReadOnly].
- Search filter: `?search_name=<name>` filters cities by name (case-insensitive contains).
- Pagination: PageNumberPagination with default page_size=10.
- URL pattern: `/api/cities/` (list/create), `/api/cities/<uuid>/` (retrieve/update/delete).
- The example curl commands in REQUIREMENTS.md show the expected API shape:
  - POST `/api/cities` with city data (admin only)
  - GET `/api/cities?search_name=Copenhagen` for searching
  - GET `/api/cities/<uuid>` for detail

**Definition of Done:**

- [ ] GET `/api/cities` returns paginated list of cities
- [ ] GET `/api/cities?search_name=Tokyo` returns filtered results
- [ ] GET `/api/cities/<uuid>` returns single city
- [ ] POST `/api/cities` with admin token creates a new city
- [ ] PUT `/api/cities/<uuid>` with admin token updates a city
- [ ] DELETE `/api/cities/<uuid>` with admin token deletes a city
- [ ] Regular user gets 403 on POST/PUT/DELETE

**Verify:**

- `docker compose exec app bash -c "curl --silent http://localhost:8000/api/cities | jq '.results | length'"` — returns number of seeded cities
- `docker compose exec app bash -c "curl --silent 'http://localhost:8000/api/cities?search_name=Tokyo' | jq '.results[0].name'"` — returns "Tokyo"

---

### Task 6: REST API — Weather Data and Forecasts

**Objective:** Create DRF viewsets for WeatherRecord (historical data) and Forecast endpoints with filtering by city and date range. Forecasts are limited to 7 days ahead.

**Dependencies:** Task 5

**Files:**

- Modify: `app/weather/serializers.py` (add WeatherRecordSerializer, ForecastSerializer)
- Modify: `app/weather/views.py` (add WeatherRecordViewSet, ForecastViewSet)
- Modify: `app/weather/urls.py` (add routes)

**Key Decisions / Notes:**

- WeatherRecordViewSet: list/retrieve only for regular users; admin can create/update/delete. Filter by city UUID (`?city=<uuid>`), date range (`?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD`). Ordered by `-recorded_at`.
- ForecastViewSet: list/retrieve for all authenticated users; admin can create. Filter by city UUID. Validation: forecast_date cannot be more than 7 days from today. Ordered by `forecast_date`.
- **7-day forecast validation:** Implement in `ForecastSerializer.validate_forecast_date()` (not just model `clean()`), because DRF serializers do not automatically call `model.full_clean()`. The serializer must explicitly enforce the 7-day limit to prevent bypass.
- URL patterns: `/api/weather-records/`, `/api/forecasts/`.
- Nested routes optional; flat routes with query param filtering is simpler.

**Definition of Done:**

- [ ] GET `/api/weather-records/?city=<uuid>` returns weather records for that city
- [ ] GET `/api/weather-records/?date_from=2026-02-01&date_to=2026-02-20` returns date-filtered records
- [ ] GET `/api/forecasts/?city=<uuid>` returns 7-day forecasts for that city
- [ ] POST `/api/forecasts/` with forecast_date > 7 days from today returns 400 validation error
- [ ] Admin can create weather records and forecasts; regular user cannot

**Verify:**

- `docker compose exec app bash -c "curl --silent http://localhost:8000/api/weather-records/ | jq '.results | length'"` — returns records count
- `docker compose exec app bash -c "curl --silent http://localhost:8000/api/forecasts/ | jq '.results[0].forecast_date'"` — returns a date string

---

### Task 7: GraphQL API

**Objective:** Implement a GraphQL API using strawberry-django with types for City, WeatherRecord, and Forecast. Support queries (list, filter, detail) and mutations (create/update/delete for admin).

**Dependencies:** Task 5, Task 6

**Files:**

- Create: `app/weather/schema.py`
- Modify: `app/config/urls.py` (add GraphQL URL)

**Key Decisions / Notes:**

- Use `strawberry_django` types mapped to Django models.
- Query types: `cities` (with optional name filter), `city(uuid)`, `weather_records(city_uuid, date_from, date_to)`, `forecasts(city_uuid)`.
- Mutation types: `create_city`, `update_city`, `delete_city`, `create_weather_record`, `create_forecast`. Mutations require admin authentication.
- Permission integration: verify `info.context.request.user` is available in resolvers by configuring strawberry-django's `GraphQLView` with Django's authentication middleware. Check `info.context.request.user.is_staff` in mutation resolvers. Wrap mutations in try/except for `IntegrityError` to return proper GraphQL errors (not 500).
- GraphQL endpoint: `/api/graphql/` with GraphiQL UI enabled in development.

**Definition of Done:**

- [ ] GraphQL endpoint at `/api/graphql/` is accessible
- [ ] Query `{ cities { uuid name country } }` returns all cities
- [ ] Query with filter `{ cities(name: "Tokyo") { uuid name } }` returns filtered results
- [ ] Mutation `createCity(input: {...})` works with admin auth, fails without
- [ ] Mutation for duplicate city returns proper GraphQL error (not 500 server error)
- [ ] Unauthenticated mutation request returns appropriate error in GraphQL format
- [ ] GraphiQL interactive UI is available at `/api/graphql/` in browser

**Verify:**

- `docker compose exec app bash -c "curl --silent --header 'Content-Type: application/json' --data '{\"query\": \"{ cities { uuid name country } }\"}' http://localhost:8000/api/graphql/ | jq '.data.cities | length'"` — returns 5

---

### Task 8: Atom Feed for Weather Forecasts

**Objective:** Implement Atom feeds for weather forecasts using Django's syndication framework. Provide a feed per city and a combined feed for all cities.

**Dependencies:** Task 6

**Files:**

- Create: `app/weather/feeds.py`
- Modify: `app/weather/urls.py` (add feed URLs)

**Key Decisions / Notes:**

- Use `django.contrib.syndication.views.Feed` with `feed_type = Atom1Feed`.
- `AllCityForecastFeed` at `/api/feeds/forecasts/` — all forecasts across all cities.
- `CityForecastFeed` at `/api/feeds/forecasts/<city_uuid>/` — forecasts for a specific city.
- Feed items are Forecast objects ordered by forecast_date.
- Each item shows: title = "City - Date: High/Low", description = weather description + indicators.
- Feed title: "WFS Weather Forecasts" / "WFS Forecasts for <City>".

**Definition of Done:**

- [ ] GET `/api/feeds/forecasts/` returns valid Atom XML with forecast entries
- [ ] GET `/api/feeds/forecasts/<city_uuid>/` returns city-specific Atom feed
- [ ] Feed XML is parseable by standard Atom/RSS readers (valid XML with proper Atom namespace)
- [ ] Feed entries contain forecast date, temperature range, and description

**Verify:**

- `docker compose exec app bash -c "curl --silent http://localhost:8000/api/feeds/forecasts/ | xmllint --format - | head -20"` — valid Atom XML
- `docker compose exec app bash -c "curl --silent http://localhost:8000/api/feeds/forecasts/ | grep -c '<entry>'"` — returns number of forecast entries

---

### Task 9: WebSocket Weather Alerts

**Objective:** Set up Django Channels with an in-memory channel layer and create a WebSocket consumer that broadcasts weather alerts to connected clients. Alerts are sent when new WeatherAlert objects are created.

**Dependencies:** Task 2

**Files:**

- Create: `app/weather/consumers.py`
- Create: `app/weather/routing.py`
- Modify: `app/config/asgi.py` (integrate Channels routing)
- Modify: `app/config/settings.py` (add CHANNEL_LAYERS with InMemoryChannelLayer)
- Create: `app/weather/signals.py` (post_save signal to broadcast alerts)

**Key Decisions / Notes:**

- Use `channels.layers.InMemoryChannelLayer` (no Redis required).
- WebSocket endpoint: `ws://localhost:8001/ws/alerts/` (general) and `ws://localhost:8001/ws/alerts/<city_uuid>/` (per-city).
- `WeatherAlertConsumer` (AsyncJsonWebsocketConsumer): joins group on connect, receives alert broadcasts.
- `post_save` signal on WeatherAlert model: use `transaction.on_commit()` to broadcast AFTER the database transaction commits (prevents ghost notifications on rollback and reduces race conditions with the in-memory layer). Broadcast to both the city-specific group and the general alerts group.
- The startup script runs Daphne on port 8001 for WebSocket (in addition to Gunicorn on 8000 for HTTP). Both run as background processes with PID tracking. If either dies, `wait -n` causes the entrypoint to exit, triggering Docker restart.
- Alert payload: `{type, city, alert_type, severity, title, description, issued_at}`.

**Definition of Done:**

- [ ] Both gunicorn (port 8000) and daphne (port 8001) processes are running: `ps aux | grep -E "(gunicorn|daphne)"` shows both
- [ ] WebSocket connection to `ws://localhost:8001/ws/alerts/` succeeds
- [ ] WebSocket connection to `ws://localhost:8001/ws/alerts/<city_uuid>/` succeeds
- [ ] Creating a new WeatherAlert via admin triggers a message to connected WebSocket clients
- [ ] WebSocket message contains alert type, severity, title, and city information
- [ ] Broadcast uses `transaction.on_commit()` to ensure it fires only after commit
- [ ] Disconnected clients do not cause errors

**Verify:**

- `docker compose exec app bash -c "ps aux | grep -E '(gunicorn|daphne)' | grep -v grep"` — shows both processes running
- `docker compose exec app bash -c "echo '{\"type\": \"ping\"}' | timeout 3 wscat -c ws://localhost:8001/ws/alerts/ 2>&1 || echo 'WebSocket endpoint exists'"` — WebSocket connection attempt completes
- `docker compose exec app python manage.py shell -c "from channels.layers import get_channel_layer; print(get_channel_layer())"` — returns InMemoryChannelLayer instance

---

### Task 10: GitHub Webhooks

**Objective:** Create a webhook endpoint that receives GitHub webhook events, validates the HMAC-SHA256 signature using the configured secret, and logs events to the WebhookEvent model.

**Dependencies:** Task 2

**Files:**

- Create: `app/weather/webhooks.py`
- Modify: `app/weather/urls.py` (add webhook URL)

**Key Decisions / Notes:**

- Endpoint: POST `/api/webhooks/github/`.
- HMAC-SHA256 validation using `WEBHOOK_SECRET` from environment (set in compose.yaml).
- Extract `X-Hub-Signature-256` header, compute expected signature, compare using `hmac.compare_digest`.
- Parse `X-GitHub-Event` header for event type.
- Store event in WebhookEvent model (event_type, payload, processed=False).
- Return 200 on success, 400 on missing signature, 403 on invalid signature.
- No authentication required (GitHub cannot send JWT tokens); security is via HMAC.
- Exempt from CSRF via `@csrf_exempt`.

**Definition of Done:**

- [ ] POST to `/api/webhooks/github/` with valid HMAC signature returns 200
- [ ] POST with invalid/missing signature returns 403/400
- [ ] Event is saved to WebhookEvent model with correct event_type and payload
- [ ] `X-GitHub-Event` header value is stored as event_type
- [ ] Endpoint is CSRF-exempt

**Verify:**

- `docker compose exec app bash -c "echo -n '{\"action\":\"opened\"}' | curl --silent --write-out '%{http_code}' --header 'Content-Type: application/json' --header 'X-GitHub-Event: push' --header 'X-Hub-Signature-256: sha256=$(echo -n '{\"action\":\"opened\"}' | openssl dgst -sha256 -hmac 'a0tObtQBvNhQjRSbPRZrIkXiooIH2ucIZJeESrRcIFyYOtSV8FKWrAri8djp3CQd' | cut -d' ' -f2)' --data '{\"action\":\"opened\"}' http://localhost:8000/api/webhooks/github/"` — returns 200

---

### Task 11: TLS Configuration and API Documentation

**Objective:** Add TLS support via self-signed certificates (toggled by TLS_ENABLE env var) and integrate drf-spectacular for OpenAPI documentation and create an AsyncAPI spec for the WebSocket API.

**Dependencies:** Task 5, Task 6, Task 9

**Files:**

- Create: `app/scripts/generate_certs.sh` (self-signed cert generation)
- Modify: `app/scripts/startup.sh` (conditional TLS, cert generation, gunicorn SSL flags)
- Create: `app/weather/openapi.py` (custom drf-spectacular extensions if needed)
- Create: `app/docs/asyncapi.yaml` (AsyncAPI 2.6 spec for WebSocket)
- Modify: `app/config/urls.py` (add Swagger/ReDoc UI URLs)
- Modify: `app/config/settings.py` (add SPECTACULAR_SETTINGS)

**Key Decisions / Notes:**

- TLS is controlled by `TLS_ENABLE` env var (0=off, 1=on, default 0 in compose.yaml).
- When TLS_ENABLE=1: startup.sh runs `generate_certs.sh` **synchronously** and verifies cert files exist BEFORE starting gunicorn/daphne. If cert generation fails, startup.sh exits with error (container will restart). Start gunicorn with `--certfile` and `--keyfile`, start daphne with `--ssl-certificate` and `--ssl-key`.
- Cert paths: `/etc/wfs/ssl/certs/` and `/etc/wfs/ssl/private/` (from Dockerfile ARGs).
- drf-spectacular: auto-generates OpenAPI 3.0 schema from DRF viewsets. Swagger UI at `/api/docs/`, ReDoc at `/api/docs/redoc/`.
- AsyncAPI spec: manually authored YAML describing WebSocket channels, message schemas, server info.
- healthcheck.sh: use `http` or `https` scheme based on `TLS_ENABLE`. Include `--insecure` flag for self-signed certs when TLS is on.

**Definition of Done:**

- [ ] With TLS_ENABLE=0: service starts on HTTP, all endpoints work
- [ ] With TLS_ENABLE=1: startup.sh generates cert synchronously before starting servers, gunicorn serves HTTPS on port 8000
- [ ] With TLS_ENABLE=1: healthcheck.sh correctly uses https scheme with --insecure flag
- [ ] GET `/api/docs/` returns Swagger UI page
- [ ] GET `/api/docs/redoc/` returns ReDoc page
- [ ] GET `/api/schema/` returns OpenAPI JSON/YAML schema
- [ ] `app/docs/asyncapi.yaml` exists, is valid YAML, and contains required AsyncAPI 2.6 keys (`asyncapi`, `info`, `channels`, `components`) describing `/ws/alerts/` and `/ws/alerts/{city_uuid}/` channels with message schemas

**Verify:**

- `docker compose exec app bash -c "curl --silent http://localhost:8000/api/schema/ | jq '.info.title'"` — returns schema title
- `docker compose exec app bash -c "curl --silent http://localhost:8000/api/docs/ | grep -o 'swagger-ui'"` — Swagger UI page loads

---

### Task 12: BDD Tests and E2E Test Scripts

**Objective:** Write django-behave feature files for key user scenarios and create curl-based E2E test scripts that exercise all API patterns.

**Dependencies:** Task 5, Task 6, Task 7, Task 8, Task 9, Task 10, Task 11

**Files:**

- Create: `app/features/__init__.py`
- Create: `app/features/environment.py` (behave-django environment setup)
- Create: `app/features/cities.feature` (city CRUD scenarios)
- Create: `app/features/weather.feature` (weather data scenarios)
- Create: `app/features/steps/__init__.py`
- Create: `app/features/steps/city_steps.py`
- Create: `app/features/steps/weather_steps.py`
- Create: `app/scripts/e2e_test.sh` (curl-based E2E tests for all APIs — at `/app/scripts/e2e_test.sh` in container)

**Key Decisions / Notes:**

- behave-django features use the Django test client (no running server needed for BDD).
- Feature scenarios: admin creates city, regular user reads city list, search city by name, create weather record, get forecasts, invalid JWT returns 401.
- `e2e_test.sh`: executable script at `app/scripts/e2e_test.sh` (runs inside container at `/app/scripts/e2e_test.sh` due to volume mount). Tests: JWT auth, city CRUD, weather records, forecasts, GraphQL query, Atom feed fetch, webhook with valid/invalid HMAC, API docs.
- E2E script prints PASS/FAIL per test, exits non-zero on any failure.
- E2E script runs inside the container: `docker compose exec app bash /app/scripts/e2e_test.sh`. Uses single quotes for JSON payloads to avoid shell escaping issues.
- E2E script uses `curl http://localhost:8000/...` (inside container, localhost resolves to the container itself).

**Definition of Done:**

- [ ] `docker compose exec app python manage.py behave --no-input` runs all BDD features and passes
- [ ] BDD features cover: city CRUD, weather record retrieval, forecast 7-day limit, authentication
- [ ] `scripts/e2e_test.sh` exercises: JWT auth, REST cities, REST weather, GraphQL, Atom feed, webhook, API docs
- [ ] E2E script reports PASS/FAIL per test case and exits with appropriate code
- [ ] All E2E tests pass against running Docker service

**Verify:**

- `docker compose exec app python manage.py behave --no-input` — all scenarios pass
- `docker compose exec app bash /app/scripts/e2e_test.sh` — all E2E tests pass

---

## Testing Strategy

- **Unit tests:** Django model validation (forecast 7-day limit, city uniqueness), permission class logic, HMAC signature validation, serializer validation. Run via `python manage.py test`.
- **BDD tests (integration):** django-behave feature files testing API flows through Django test client. Run via `python manage.py behave --no-input`.
- **E2E tests:** curl-based scripts against live Docker containers testing all API patterns end-to-end. Run via `scripts/e2e_test.sh`.
- **Manual verification:** Django admin at `/admin/`, Swagger UI at `/api/docs/`, GraphiQL at `/api/graphql/`.

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Redis service referenced but not defined in compose.yaml** | CRITICAL | CRITICAL | **Task 1 MUST remove redis from compose.yaml `depends_on` list** — compose.yaml currently contains `depends_on: - postgres - redis` but redis service is never defined. Docker Compose will fail immediately with "service redis is not defined" error. Verification: Task 1 DoD includes `docker compose config --quiet` to validate compose before build. |
| **Dockerfile path confusion will cause runtime failures** | CRITICAL | CRITICAL | **Task 1 verification MUST explicitly test script paths:** `docker compose exec app ls /app/scripts/startup.sh` and `docker compose exec app test -x /app/scripts/healthcheck.sh`. Volume mount `./app:/app` overrides `/app` contents at runtime — scripts must be accessible at `/app/scripts/` after mount, not `/app/app/scripts/`. |
| **Dual-server process (Gunicorn + Daphne) fragile if one dies** | HIGH | HIGH | startup.sh runs both as background jobs with PID tracking. Implements `wait -n` to exit if either dies (Docker restarts container automatically). **Task 9 DoD must verify both processes running:** `docker compose exec app ps aux \| grep -E "(gunicorn\|daphne)"` shows 2 processes. healthcheck.sh checks **BOTH** ports: `curl localhost:8000 && nc -zv localhost 8001`. |
| In-memory channel layer drops messages under load | Low | Med | E2E test script (`app/scripts/e2e_test.sh`) adds `sleep 2` after creating WeatherAlert via admin API before checking WebSocket receipt. Signal handler (`app/weather/signals.py`) uses `transaction.on_commit(lambda: channel_layer.group_send(...))` to ensure broadcast AFTER commit (prevents ghost notifications on rollback). **Task 9 DoD:** Unit test verifies broadcast only on committed transaction. |
| **7-day forecast validation bypassed in API layer** | MED | HIGH | **Task 6 MUST implement ForecastSerializer.validate_forecast_date()** explicitly — DRF serializers don't auto-call model.clean(). Do NOT rely solely on model validation. **Task 6 DoD:** Unit test verifies `POST /api/forecasts/ with forecast_date > 7 days returns 400` (not stored in DB). |
| **GraphQL mutation authentication not enforced** | MED | HIGH | **Task 7 MUST include unit test** verifying `info.context.request.user` is available in mutation resolvers. Test unauthenticated mutation and verify permission error returned (not null user). Wrap mutations in try/except for IntegrityError to return proper GraphQL error format. |
| **Webhook endpoint vulnerable to DoS** | LOW | MED | **Task 10 implements rate limiting:** 10 requests/minute per IP using Django cache. Use `@ratelimit()` decorator or IP-based cache key. **DoD:** `curl` loop test verifies rate limiting kicks in after 10 requests. |
| strawberry-django compatibility with Django 5.x | Low | Med | Pin `strawberry-graphql-django>=0.20,<1.0` in `requirements.txt`. Pin Django to `>=5.0,<5.2`. **Task 1 DoD:** `python manage.py shell -c "import strawberry"` succeeds. |
| django-behave compatibility with Django 5.x | Low | Med | Pin `behave-django>=1.4` in `requirements.txt` (first version supporting Django 5.x). **Task 1 DoD:** `python manage.py behave --help` runs without import errors. **Task 12 DoD:** BDD tests execute successfully. |
| Self-signed TLS certs cause curl errors | Low | Low | E2E scripts use `--insecure` flag when `TLS_ENABLE=1`. `healthcheck.sh` uses `--insecure` for self-signed certs. Document in startup logs that certs are self-signed. |
| PostgreSQL not ready when app starts | Med | Low | **compose.yaml uses `depends_on: postgres: condition: service_healthy`** to ensure postgres is healthy before app starts (not just started). startup.sh also implements `until pg_isready; do sleep 1; done` wait loop with 30-second timeout as defense-in-depth. |
| **TLS cert generation timing issue** | MED | HIGH | **Task 11 startup.sh generates certs SYNCHRONOUSLY before starting servers** — never in background. Verifies cert files exist before calling gunicorn/daphne. If generation fails (openssl error), startup.sh exits with error code and container fails to start (correct behavior). **healthcheck.sh includes `sleep 2` initial delay** for cert generation. **Task 11 DoD:** With `TLS_ENABLE=1`, container waits for certs before healthcheck. |

## Open Questions

- None remaining — all design decisions resolved.

### Deferred Ideas

- Integration with a real weather API (Open-Meteo or OpenWeatherMap) for live data
- Redis-backed channel layer for production-grade WebSocket support
- API rate limiting and throttling
- Frontend dashboard for weather data visualization
- GitHub Codespaces devcontainer.json configuration
- CI/CD pipeline configuration
