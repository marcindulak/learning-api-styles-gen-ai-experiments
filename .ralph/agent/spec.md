# Weather Forecast Service — Specification

## Summary

A Django-based monolithic web application that exposes weather data for the world's 5 largest cities (by population) through REST, GraphQL, Atom feed, and WebSocket APIs, with JWT authentication, an admin CMS, GitHub webhook integration, and optional TLS — all running in Docker containers.

---

## 1. Domain Model

### 1.1 City

| Field      | Type           | Constraints                                    |
|------------|----------------|------------------------------------------------|
| uuid       | UUID v4        | Primary key, auto-generated, immutable         |
| name       | string         | Max 100 chars, required, unique                |
| country    | string         | Max 100 chars, required                        |
| region     | string         | Max 100 chars, required                        |
| timezone   | string         | Valid IANA timezone (e.g. `Asia/Tokyo`), required |
| latitude   | decimal        | -90.0 to 90.0, 6 decimal places, required     |
| longitude  | decimal        | -180.0 to 180.0, 6 decimal places, required   |
| created_at | datetime (UTC) | Auto-set on creation                           |
| updated_at | datetime (UTC) | Auto-set on update                             |

**Seed data (5 biggest cities by population):**

| Name        | Country   | Region        | Timezone           | Latitude  | Longitude  |
|-------------|-----------|---------------|--------------------|-----------|------------|
| Tokyo       | Japan     | Asia          | Asia/Tokyo         | 35.689500 | 139.691700 |
| Delhi       | India     | Asia          | Asia/Kolkata       | 28.613900 | 77.209000  |
| Shanghai    | China     | Asia          | Asia/Shanghai      | 31.230400 | 121.473700 |
| São Paulo   | Brazil    | South America | America/Sao_Paulo  | -23.550500| -46.633300 |
| Mexico City | Mexico    | North America | America/Mexico_City| 19.432600 | -99.133200 |

### 1.2 WeatherRecord

| Field              | Type           | Constraints                              |
|--------------------|----------------|------------------------------------------|
| uuid               | UUID v4        | Primary key, auto-generated              |
| city               | FK → City      | Required, on_delete=CASCADE              |
| timestamp          | datetime (UTC) | Required, indexed                        |
| temperature        | decimal        | °C, 1 decimal place                      |
| feels_like         | decimal        | °C, 1 decimal place                      |
| humidity           | integer        | 0–100 (%)                                |
| pressure           | decimal        | hPa, 1 decimal place                     |
| wind_speed         | decimal        | m/s, 1 decimal place                     |
| wind_direction     | integer        | 0–360 (degrees)                          |
| precipitation      | decimal        | mm, 1 decimal place, default 0.0         |
| visibility         | integer        | meters, 0–100000                         |
| uv_index           | decimal        | 0.0–15.0, 1 decimal place               |
| cloud_cover        | integer        | 0–100 (%)                                |
| description        | string         | Max 200 chars (e.g. "Partly cloudy")     |
| created_at         | datetime (UTC) | Auto-set on creation                     |

**Constraints:**
- Unique together: (city, timestamp) — no duplicate readings for same city at same time.
- `timestamp` must not be more than 7 days in the future from the current date.

### 1.3 WeatherForecast

| Field              | Type           | Constraints                              |
|--------------------|----------------|------------------------------------------|
| uuid               | UUID v4        | Primary key, auto-generated              |
| city               | FK → City      | Required, on_delete=CASCADE              |
| forecast_date      | date           | Required, indexed                        |
| temperature_high   | decimal        | °C, 1 decimal place                      |
| temperature_low    | decimal        | °C, 1 decimal place                      |
| humidity           | integer        | 0–100 (%)                                |
| precipitation_prob | integer        | 0–100 (%)                                |
| wind_speed         | decimal        | m/s, 1 decimal place                     |
| description        | string         | Max 200 chars                            |
| created_at         | datetime (UTC) | Auto-set on creation                     |
| updated_at         | datetime (UTC) | Auto-set on update                       |

**Constraints:**
- Unique together: (city, forecast_date).
- `forecast_date` must be within 7 days from today (inclusive).
- `temperature_high` >= `temperature_low`.

### 1.4 WeatherAlert

| Field       | Type           | Constraints                                      |
|-------------|----------------|--------------------------------------------------|
| uuid        | UUID v4        | Primary key, auto-generated                      |
| city        | FK → City      | Required, on_delete=CASCADE                      |
| severity    | string (enum)  | One of: `advisory`, `watch`, `warning`, `emergency` |
| event       | string         | Max 200 chars (e.g. "Severe Thunderstorm")       |
| description | text           | Required                                         |
| starts_at   | datetime (UTC) | Required                                         |
| expires_at  | datetime (UTC) | Required, must be > starts_at                    |
| active      | boolean        | Default true                                     |
| created_at  | datetime (UTC) | Auto-set on creation                             |

### 1.5 User Roles

| Role    | Permissions                                                                |
|---------|----------------------------------------------------------------------------|
| admin   | Full CRUD on all models; access to Django admin CMS; manage users          |
| regular | Read-only access to cities, weather records, forecasts, and alerts         |

**Seed data:**
- Admin user: username=`admin`, password=`admin` (as shown in curl examples).

---

## 2. REST API

**Base path:** `/api`

**Authentication:** JWT via `Authorization: Bearer <token>` header.

### 2.1 JWT Endpoints

#### POST `/api/jwt/obtain`

- **Given** valid credentials `{"username": "admin", "password": "admin"}`
- **When** POST to `/api/jwt/obtain` with Content-Type `application/json`
- **Then** return 200 with `{"access": "<jwt>", "refresh": "<jwt>"}`

- **Given** invalid credentials
- **When** POST to `/api/jwt/obtain`
- **Then** return 401 with `{"detail": "No active account found with the given credentials"}`

#### POST `/api/jwt/refresh`

- **Given** a valid refresh token `{"refresh": "<jwt>"}`
- **When** POST to `/api/jwt/refresh`
- **Then** return 200 with `{"access": "<jwt>"}`

- **Given** an expired or invalid refresh token
- **When** POST to `/api/jwt/refresh`
- **Then** return 401

### 2.2 City Endpoints

#### GET `/api/cities`

- **Given** any user (authenticated or anonymous)
- **When** GET `/api/cities`
- **Then** return 200 with paginated list: `{"count": N, "next": null|url, "previous": null|url, "results": [...]}`
- Each result contains: uuid, name, country, region, timezone, latitude, longitude

- **Given** query parameter `search_name=Tokyo`
- **When** GET `/api/cities?search_name=Tokyo`
- **Then** return only cities whose name contains "Tokyo" (case-insensitive)

#### GET `/api/cities/{uuid}`

- **Given** a valid city UUID
- **When** GET `/api/cities/{uuid}`
- **Then** return 200 with city object

- **Given** a non-existent UUID
- **When** GET `/api/cities/{uuid}`
- **Then** return 404

#### POST `/api/cities`

- **Given** admin user with valid JWT
- **When** POST with valid city payload
- **Then** return 201 with created city object including generated uuid

- **Given** regular user or anonymous
- **When** POST to `/api/cities`
- **Then** return 403 (regular) or 401 (anonymous)

- **Given** missing required fields
- **When** POST to `/api/cities`
- **Then** return 400 with field-level validation errors

- **Given** duplicate city name
- **When** POST to `/api/cities`
- **Then** return 400 with uniqueness error

#### PUT `/api/cities/{uuid}`

- **Given** admin user with valid JWT and valid payload
- **When** PUT to `/api/cities/{uuid}`
- **Then** return 200 with updated city

- **Given** non-admin user
- **When** PUT to `/api/cities/{uuid}`
- **Then** return 403 or 401

#### PATCH `/api/cities/{uuid}`

- Same authorization rules as PUT
- Partial update

#### DELETE `/api/cities/{uuid}`

- **Given** admin user
- **When** DELETE `/api/cities/{uuid}`
- **Then** return 204 (no content), cascade-delete associated weather data

- **Given** non-admin user
- **When** DELETE `/api/cities/{uuid}`
- **Then** return 403 or 401

### 2.3 Weather Record Endpoints

#### GET `/api/cities/{city_uuid}/weather`

- **Given** valid city UUID
- **When** GET with optional query params: `from` (ISO date), `to` (ISO date)
- **Then** return 200 with paginated weather records for that city, ordered by timestamp descending

- **Given** invalid city UUID
- **Then** return 404

#### GET `/api/cities/{city_uuid}/weather/{record_uuid}`

- **Given** valid city UUID and record UUID
- **When** GET
- **Then** return 200 with single weather record

#### POST `/api/cities/{city_uuid}/weather`

- **Given** admin user
- **When** POST with valid weather record payload (timestamp, temperature, humidity, etc.)
- **Then** return 201 with created record

- **Given** duplicate (city, timestamp) combination
- **Then** return 400

### 2.4 Weather Forecast Endpoints

#### GET `/api/cities/{city_uuid}/forecast`

- **Given** valid city UUID
- **When** GET
- **Then** return 200 with list of forecasts for next 7 days, ordered by forecast_date ascending

#### POST `/api/cities/{city_uuid}/forecast`

- **Given** admin user, valid payload
- **When** POST
- **Then** return 201

- **Given** forecast_date more than 7 days from today
- **Then** return 400 with validation error

- **Given** temperature_high < temperature_low
- **Then** return 400 with validation error

### 2.5 Weather Alert Endpoints

#### GET `/api/alerts`

- Return all active alerts, paginated
- Optional filter: `?city={city_uuid}`, `?severity=warning`

#### POST `/api/alerts`

- Admin only. Return 201.

#### GET `/api/alerts/{uuid}`

- Return single alert.

#### PATCH `/api/alerts/{uuid}`

- Admin only. Used to deactivate alerts (`{"active": false}`).

---

## 3. GraphQL API

**Endpoint:** `/api/graphql`

### Queries

```graphql
type Query {
  cities: [City!]!
  city(uuid: UUID!): City
  weatherRecords(cityUuid: UUID!, from: DateTime, to: DateTime): [WeatherRecord!]!
  forecasts(cityUuid: UUID!): [Forecast!]!
  alerts(cityUuid: UUID, active: Boolean): [Alert!]!
}
```

### Mutations (admin only)

```graphql
type Mutation {
  createCity(input: CityInput!): City!
  updateCity(uuid: UUID!, input: CityInput!): City!
  deleteCity(uuid: UUID!): Boolean!
  createWeatherRecord(cityUuid: UUID!, input: WeatherRecordInput!): WeatherRecord!
  createForecast(cityUuid: UUID!, input: ForecastInput!): Forecast!
  createAlert(input: AlertInput!): Alert!
}
```

### Acceptance Criteria

- **Given** a valid GraphQL query for cities
- **When** POST to `/api/graphql` with `{"query": "{ cities { uuid name country } }"}`
- **Then** return 200 with `{"data": {"cities": [...]}}`

- **Given** an unauthenticated mutation request
- **When** POST to `/api/graphql`
- **Then** return errors with "Authentication required" message

- **Given** a regular user attempting a mutation
- **When** POST to `/api/graphql`
- **Then** return errors with "Permission denied" message

---

## 4. Atom Feed API

**Endpoint:** `/api/feed/forecasts`

### Acceptance Criteria

- **Given** forecast data exists
- **When** GET `/api/feed/forecasts`
- **Then** return `Content-Type: application/atom+xml` with valid Atom 1.0 XML
- Feed title: "Weather Forecast Service — Forecasts"
- Each entry: one forecast per city per day
- Entries ordered by updated timestamp descending
- Each entry contains: title (city + date), summary (description, high/low temp), updated timestamp, unique id

- **Given** optional query param `?city={city_uuid}`
- **When** GET `/api/feed/forecasts?city={uuid}`
- **Then** return only forecasts for that city

---

## 5. WebSocket API

**Port:** 8001
**Path:** `ws://localhost:8001/ws/alerts`

### Acceptance Criteria

- **Given** a WebSocket client connects to `ws://localhost:8001/ws/alerts`
- **When** connection is established
- **Then** server sends a welcome message: `{"type": "connection_established"}`

- **Given** a connected client
- **When** a new alert is created via REST or GraphQL
- **Then** all connected clients receive: `{"type": "alert", "data": {"uuid": "...", "city": "...", "severity": "...", "event": "...", "description": "..."}}`

- **Given** a connected client with subscription filter `{"type": "subscribe", "city_uuid": "..."}`
- **When** an alert is created for that city
- **Then** only subscribed clients receive the alert

- **Given** a connected client
- **When** connection is idle for 60 seconds
- **Then** server sends a ping; client must respond with pong within 10 seconds or be disconnected

---

## 6. GitHub Webhook Integration

**Endpoint:** POST `/api/webhooks/github`

### Acceptance Criteria

- **Given** a valid webhook payload with correct `X-Hub-Signature-256` header (HMAC-SHA256 using `WEBHOOK_SECRET`)
- **When** POST to `/api/webhooks/github`
- **Then** return 200 with `{"status": "ok"}`
- The service logs the event type and payload summary

- **Given** missing or invalid signature
- **When** POST to `/api/webhooks/github`
- **Then** return 403 with `{"detail": "Invalid signature"}`

- **Given** a `ping` event
- **When** POST with valid signature
- **Then** return 200 with `{"status": "pong"}`

- **Given** a `push` event
- **When** POST with valid signature
- **Then** return 200, log commit info

---

## 7. Admin CMS

**Endpoint:** `/admin/`

### Acceptance Criteria

- **Given** Django's built-in admin site
- **When** admin user navigates to `/admin/`
- **Then** they see management interfaces for: Cities, Weather Records, Forecasts, Alerts, Users

- **Given** a regular user
- **When** they attempt to access `/admin/`
- **Then** they are redirected to the admin login page; upon login they see no models (no staff permissions)

- City admin: list display shows name, country, region; search by name; filter by region
- WeatherRecord admin: list display shows city, timestamp, temperature; filter by city, date range
- Forecast admin: list display shows city, forecast_date, temp high/low; filter by city
- Alert admin: list display shows city, severity, event, active; filter by severity, active

---

## 8. Infrastructure & Deployment

### 8.1 Docker Services

| Service  | Image               | Container         | Port(s)        | Network          |
|----------|---------------------|--------------------|----------------|------------------|
| app      | django/app          | django-app         | 8000, 8001     | django_internal  |
| postgres | postgres:17-alpine  | django-postgres    | 5432           | django_internal  |
| redis    | redis:7-alpine      | django-redis       | 6379           | django_internal  |

**Note:** The `redis` service must be added to `compose.yaml` (currently referenced in `depends_on` but not defined).

### 8.2 Startup Script (`app/scripts/startup.sh`)

- **Given** the container starts
- **When** `startup.sh` executes
- **Then** it:
  1. Waits for PostgreSQL to be ready
  2. Runs `python manage.py migrate --no-input`
  3. Creates superuser `admin`/`admin` if it doesn't exist (using `createsuperuser --no-input` with `DJANGO_SUPERUSER_*` env vars)
  4. Loads seed data (5 cities) if no cities exist
  5. Optionally generates TLS certificates if `TLS_ENABLE=1`
  6. Starts Django development server on `0.0.0.0:8000`
  7. Starts WebSocket server on `0.0.0.0:8001`

### 8.3 Health Check (`app/scripts/healthcheck.sh`)

- **Given** the container is running
- **When** health check executes
- **Then** it curls `http://localhost:8000/api/health` and checks for HTTP 200

### 8.4 Build & Run

```bash
docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)
docker compose up --detach --wait
```

### 8.5 TLS (Optional)

- **Given** `TLS_ENABLE=1`
- **When** the container starts
- **Then** generate a self-signed certificate in `APP_TLS_CERTS_DIR` and serve HTTPS on port 8000

- **Given** `TLS_ENABLE=0` (default)
- **Then** serve plain HTTP

---

## 9. Django Project Structure

```
app/
├── manage.py
├── requirements.txt
├── config/
│   ├── __init__.py
│   ├── base.py          # Common settings
│   ├── postgres.py      # PostgreSQL-specific settings (DJANGO_SETTINGS_MODULE=config.postgres)
│   ├── urls.py          # Root URL configuration
│   ├── asgi.py
│   └── wsgi.py
├── weather/
│   ├── __init__.py
│   ├── models.py        # City, WeatherRecord, WeatherForecast, WeatherAlert
│   ├── serializers.py   # DRF serializers
│   ├── views.py         # DRF viewsets
│   ├── urls.py          # REST API routes
│   ├── admin.py         # Admin site registration
│   ├── schema.py        # GraphQL schema (Strawberry or Graphene)
│   ├── consumers.py     # WebSocket consumers (Django Channels)
│   ├── routing.py       # WebSocket routing
│   ├── feeds.py         # Atom feed
│   ├── webhooks.py      # GitHub webhook handler
│   ├── permissions.py   # Custom DRF permissions (IsAdminOrReadOnly)
│   ├── signals.py       # Signal to broadcast alerts via WebSocket
│   ├── management/
│   │   └── commands/
│   │       └── seed_cities.py  # Management command to seed 5 cities
│   └── tests/
│       ├── __init__.py
│       └── ...
├── features/            # behave-django BDD tests
│   ├── steps/
│   │   └── ...
│   └── *.feature
└── scripts/
    ├── startup.sh
    └── healthcheck.sh
```

---

## 10. Key Python Dependencies

| Package                  | Purpose                           |
|--------------------------|-----------------------------------|
| django                   | Web framework                     |
| djangorestframework      | REST API                          |
| djangorestframework-simplejwt | JWT authentication           |
| django-filter            | Queryset filtering                |
| channels                 | WebSocket support (ASGI)          |
| channels-redis           | Channel layer backend             |
| strawberry-graphql-django or graphene-django | GraphQL API       |
| psycopg[binary]          | PostgreSQL adapter                |
| behave-django            | BDD testing                       |
| gunicorn                 | WSGI server (optional, dev can use runserver) |
| daphne                   | ASGI server for WebSocket         |

---

## 11. Health Endpoint

#### GET `/api/health`

- **Given** the application is running and database is accessible
- **When** GET `/api/health`
- **Then** return 200 with `{"status": "ok"}`

- **Given** the database is unreachable
- **When** GET `/api/health`
- **Then** return 503 with `{"status": "error", "detail": "Database unavailable"}`

---

## 12. Edge Cases & Error Conditions

| Scenario | Expected Behavior |
|----------|-------------------|
| Invalid UUID format in URL | 404 (DRF default) |
| Request body is not valid JSON | 400 with parse error |
| JWT token expired | 401 with `{"detail": "Given token not valid for any token type", ...}` |
| Latitude out of range (-90 to 90) | 400 with validation error on `latitude` field |
| Longitude out of range (-180 to 180) | 400 with validation error on `longitude` field |
| Timezone not a valid IANA timezone | 400 with validation error |
| forecast_date > today + 7 days | 400 with "Forecast date must be within 7 days" |
| temperature_high < temperature_low | 400 with "High temperature must be >= low temperature" |
| Duplicate (city, timestamp) weather record | 400 with uniqueness constraint error |
| DELETE city with associated weather data | 204 — cascade deletes associated records |
| Empty database, GET /api/cities | 200 with `{"count": 0, "results": []}` |
| WebSocket connect to invalid path | Connection rejected |
| Webhook with unsupported event type | 200 (acknowledge but no action) |
| Pagination: page beyond range | 404 with "Invalid page" |

---

## 13. Non-Functional Requirements

| Requirement | Implementation |
|-------------|---------------|
| Portability | Docker containers; compose.yaml orchestration |
| Security | JWT auth; TLS optional; HMAC webhook verification; no hardcoded secrets in code (env vars) |
| Deployability | Single `docker compose up`; monolith |
| Testability | behave-django BDD tests; curl-based e2e tests; Django TestCase unit tests |
| Documentability | OpenAPI schema auto-generated via DRF at `/api/schema`; AsyncAPI spec for WebSocket (static YAML) |
| Runnable by readers | GitHub Codespaces compatible; standard Docker workflow |

---

## 14. Out of Scope

- **Real 3rd-party weather API integration** in this initial spec — weather data will be admin-entered or seeded. Integration with external weather APIs (e.g., OpenWeatherMap) is a future enhancement.
- **Rate limiting** — not required for an educational project.
- **Email notifications** — not mentioned in requirements.
- **Multi-language / i18n** — not required.
- **Frontend / UI** — only admin CMS (Django admin) and APIs.
- **CI/CD pipeline** — deployment is manual via Docker Compose.
- **Database backups** — not in scope.
- **Horizontal scaling** — single-container monolith by design.

---

## 15. Acceptance Test Plan

### 15.1 BDD Tests (behave-django)

Feature files covering:
1. City CRUD operations
2. Weather record creation and retrieval
3. Forecast validation (7-day limit, temp high >= low)
4. Alert creation and WebSocket broadcast
5. Authentication and authorization (admin vs regular user)
6. Webhook signature verification

### 15.2 E2E Tests (curl)

As documented in the objective:
1. Obtain JWT token
2. Create a city
3. Search cities by name
4. Retrieve a city by UUID
5. Create weather records
6. Retrieve forecasts
7. Test webhook with valid/invalid signatures
8. Test unauthorized access returns 401/403
