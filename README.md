# Weather Forecast Service

A Django monolith that exposes weather data through multiple web API styles: REST, GraphQL, WebSocket, Atom feed, and GitHub Webhooks.

Built as an educational reference for the book *Web APIs: From Zero to Production*, it covers the five biggest cities in the world with live data from the [Open-Meteo](https://open-meteo.com/) API (no key required).

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.13 |
| Framework | Django 5.1 + Daphne (ASGI) |
| REST API | Django REST Framework + SimpleJWT |
| GraphQL | Strawberry |
| WebSocket | Django Channels + Redis |
| Atom feed | Django syndication framework |
| Database | PostgreSQL 17 |
| Message broker | Redis 7 |
| Containers | Docker + Docker Compose |
| Tests | behave-django (BDD) |
| API docs | drf-spectacular (OpenAPI) + AsyncAPI |

## Quick Start

```bash
docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)
docker compose up --detach --wait
```

The app starts on `http://localhost:8000`. An `admin` superuser (password `admin`) is created automatically on first boot.

Seed the five biggest cities and fetch their 7-day forecasts from Open-Meteo:

```bash
docker compose exec app bash -c "cd /app/app && python manage.py seed_cities"
```

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /health/` | Health check |
| `POST /api/jwt/obtain` | Obtain JWT access + refresh tokens |
| `POST /api/jwt/refresh` | Refresh JWT access token |
| `GET/POST /api/cities/` | List or create cities |
| `GET /api/cities/{uuid}/` | Retrieve a city |
| `GET /api/cities/{uuid}/forecasts/` | 7-day forecast for a city |
| `GET /api/cities/{uuid}/records/` | Historical weather records for a city |
| `POST /api/cities/{uuid}/import-forecast/` | Pull latest forecast from Open-Meteo |
| `GET/POST /api/records/` | Weather records |
| `GET/POST /api/forecasts/` | Weather forecasts |
| `GET/POST /api/alerts/` | Weather alerts |
| `POST /api/webhooks/github/` | GitHub webhook receiver (HMAC-SHA256) |
| `POST /graphql/` | GraphQL API (Strawberry) |
| `GET /feed/forecasts/` | Atom feed of weather forecasts |
| `GET /api/schema/` | OpenAPI schema (YAML) |
| `GET /api/docs/` | Swagger UI |
| `WS /ws/alerts/{cityUuid}/` | WebSocket stream for city alerts |
| `GET /admin/` | Django admin (CMS) |

## Authentication

The REST API uses JWT bearer tokens. Obtain a token:

```bash
ACCESS_TOKEN=$(docker compose exec app bash -c \
  "curl --silent --request POST \
    --header 'Content-Type: application/json' \
    --data '{\"username\":\"admin\",\"password\":\"admin\"}' \
    http://localhost:8000/api/jwt/obtain | jq -r '.access'")
```

Read operations (GET) are open to unauthenticated users. Write operations require an `is_staff` user.

## Example: City CRUD

```bash
# Create a city (requires admin JWT)
docker compose exec app bash -c \
  "curl --silent --request POST \
    --header 'Authorization: Bearer $ACCESS_TOKEN' \
    --header 'Content-Type: application/json' \
    --data '{\"name\":\"Copenhagen\",\"country\":\"Denmark\",\"region\":\"Europe\",
             \"timezone\":\"Europe/Copenhagen\",\"latitude\":55.6761,\"longitude\":12.5683}' \
    http://localhost:8000/api/cities/ | jq"

# List cities with search
docker compose exec app bash -c \
  "curl --silent 'http://localhost:8000/api/cities/?search_name=Copenhagen' | jq"

# Fetch by UUID
CITY_UUID=$(docker compose exec app bash -c \
  "curl --silent 'http://localhost:8000/api/cities/?search_name=Copenhagen' | \
   jq -r '.results[0].uuid'")
docker compose exec app bash -c \
  "curl --silent http://localhost:8000/api/cities/$CITY_UUID | jq"
```

## Example: GraphQL

```bash
curl --silent --request POST \
  --header 'Content-Type: application/json' \
  --data '{"query": "{ cities { uuid name country } }"}' \
  http://localhost:8000/graphql/ | jq
```

## Example: WebSocket Alerts

```bash
# Subscribe to alerts for a city (node-ws is included in the Docker image)
docker compose exec app bash -c \
  "ws ws://localhost:8000/ws/alerts/<city-uuid>/"
```

## Running the Tests

```bash
docker compose exec app bash -c "cd /app/app && python manage.py behave --no-input"
```

## Project Layout

```
.
├── Dockerfile
├── compose.yaml
├── requirements.txt          # Python dependencies
├── app/
│   └── app/
│       ├── manage.py
│       ├── config/
│       │   ├── settings.py   # Base settings
│       │   ├── postgres.py   # Production settings (PostgreSQL)
│       │   ├── asgi.py       # ASGI + Channels routing
│       │   └── urls.py       # URL conf
│       ├── weather/
│       │   ├── models.py     # City, WeatherRecord, WeatherForecast, WeatherAlert
│       │   ├── views.py      # REST ViewSets + GitHub webhook
│       │   ├── schema.py     # GraphQL schema (Strawberry)
│       │   ├── consumers.py  # WebSocket consumer (Channels)
│       │   ├── feeds.py      # Atom feed
│       │   ├── services.py   # Open-Meteo client
│       │   ├── serializers.py
│       │   ├── permissions.py
│       │   └── management/commands/seed_cities.py
│       └── features/         # behave-django BDD tests
│           ├── cities.feature
│           └── steps/steps.py
└── docs/
    └── api/
        └── asyncapi.yaml     # AsyncAPI spec for WebSocket
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | (insecure default) | Django secret key — override in production |
| `DEBUG` | `False` | Django debug mode |
| `POSTGRES_DB` | `weather_forecast_service` | Database name |
| `POSTGRES_HOST` | `postgres` | Database host |
| `POSTGRES_USER` | `postgres` | Database user |
| `POSTGRES_PASSWORD` | `postgres` | Database password — override in production |
| `REDIS_HOST` | `redis` | Redis host |
| `WEBHOOK_SECRET` | (insecure default) | HMAC secret for GitHub webhooks — override in production |
| `TLS_ENABLE` | `0` | Set to `1` to enable TLS in Daphne |
