# Weather Forecast Service

A Django-based weather forecast service demonstrating multiple web API patterns including REST, GraphQL, WebSocket, Atom feeds, and GitHub webhooks integration.

## Architecture

- **Framework**: Django 5.1.5 with PostgreSQL 16
- **Deployment**: Docker containers (monolith architecture)
- **Testing**: Behave BDD framework with behave-django
- **APIs**: REST (DRF), GraphQL (graphene-django), WebSocket (Django Channels), Atom feeds
- **Authentication**: JWT tokens (djangorestframework-simplejwt)
- **Documentation**: OpenAPI 3.0 specification via drf-spectacular

## Features

### Functional Requirements

- User management with admin and regular user roles
- City management (limited to 5 biggest cities in the world)
- Weather data storage with historical records
- Weather forecasts (up to 7 days)
- REST API for weather indicators with JWT authentication
- GraphQL API for flexible queries
- Atom feed for weather forecast subscriptions
- WebSocket API for real-time weather alerts
- GitHub webhooks integration
- Django admin CMS for content management
- Third-party weather API integration (OpenWeatherMap)

### Non-Functional Requirements

- Containerized deployment using Docker
- Optional TLS security (HTTP/HTTPS support)
- Monolith deployment architecture
- End-to-end testable via behave and curl
- OpenAPI documentation

## Prerequisites

- Docker
- Docker Compose

## Quick Start

### 1. Build the containers

```bash
docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)
```

### 2. Start the service

```bash
docker compose up --detach --wait
```

The service will be available at `http://localhost:8000`

### 3. Run tests

```bash
docker compose exec app python manage.py behave --no-input
```

### 4. Stop the service

```bash
docker compose down
```

## API Endpoints

### REST API

Base URL: `http://localhost:8000/api`

#### Authentication

Obtain JWT token:

```bash
CREDENTIALS_PAYLOAD='{"username":"admin","password":"admin"}'
ACCESS_TOKEN=$(docker compose exec app bash -c \
  "curl \
  --data '$CREDENTIALS_PAYLOAD' \
  --header 'Content-Type: application/json' \
  --request 'POST' \
  --silent 'http://localhost:8000/api/jwt/obtain' | \
  jq --raw-output '.access'")
```

#### Cities

Create city:

```bash
CREATE_CITY_PAYLOAD='{"name":"Copenhagen","country":"Denmark","region":"Europe","timezone":"Europe/Copenhagen","latitude":55.676100,"longitude":12.568300}'
docker compose exec app bash -c \
  "curl \
  --data '$CREATE_CITY_PAYLOAD' \
  --header 'Authorization: Bearer $ACCESS_TOKEN' \
  --header 'Content-Type: application/json' \
  --request 'POST' \
  --silent \
  'http://localhost:8000/api/cities' | \
  jq"
```

List cities:

```bash
docker compose exec app bash -c \
  "curl --request 'GET' --silent 'http://localhost:8000/api/cities' | jq"
```

Search cities:

```bash
docker compose exec app bash -c \
  "curl --request 'GET' --silent 'http://localhost:8000/api/cities?search=Copenhagen' | jq"
```

Get city by UUID:

```bash
CITY_UUID=$(docker compose exec app bash -c \
  "curl --request 'GET' --silent 'http://localhost:8000/api/cities?search=Copenhagen' | \
  jq --raw-output '.results[0].uuid'")
docker compose exec app bash -c \
  "curl \
  --request 'GET' \
  --silent \
  'http://localhost:8000/api/cities/$CITY_UUID' | \
  jq"
```

### GraphQL API

Endpoint: `http://localhost:8000/api/graphql`

Interactive GraphiQL interface available at the same URL in browser.

Example query:

```graphql
{
  cities {
    name
    country
    latitude
    longitude
  }
}
```

### Atom Feed

Subscribe to weather forecasts:

```bash
curl http://localhost:8000/api/feed/forecast
```

### WebSocket API

Connect to weather alerts:

```
ws://localhost:8000/ws/alerts
```

Subscribe to city alerts:

```json
{
  "action": "subscribe",
  "city": "Tokyo"
}
```

### GitHub Webhooks

Endpoint: `http://localhost:8000/api/webhooks/github`

Configure in GitHub repository settings to receive push, issue, and pull request events.

## Documentation

### OpenAPI Specification

- Schema (JSON): `http://localhost:8000/api/schema`
- Swagger UI: `http://localhost:8000/api/docs`

### Django Admin

Access admin interface at `http://localhost:8000/admin`

Default credentials:
- Username: `admin`
- Password: `admin`

## TLS Support

Enable HTTPS by setting environment variable:

```bash
TLS_ENABLE=1 docker compose up --detach --wait
```

HTTPS endpoint: `https://localhost:8443`

## Project Structure

```
/vagrant
├── app/                          # Django application
│   ├── config/                   # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── asgi.py
│   └── weather_service/          # Main application
│       ├── models.py             # City, WeatherRecord, WeatherForecast
│       ├── serializers.py        # DRF serializers
│       ├── views.py              # REST API views
│       ├── schema.py             # GraphQL schema
│       ├── consumers.py          # WebSocket consumers
│       ├── routing.py            # WebSocket routing
│       ├── admin.py              # Django admin configuration
│       └── weather_api.py        # Third-party API client
├── features/                     # BDD feature files
│   ├── *.feature                 # Gherkin scenarios
│   ├── steps/                    # Step definitions
│   └── environment.py            # Behave configuration
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── REQUIREMENTS.md
└── README.md
```

## Environment Variables

- `WEATHER_API_KEY`: OpenWeatherMap API key (default: empty)
- `WEATHER_API_BASE_URL`: Weather API base URL (default: https://api.openweathermap.org/data/2.5)
- `WEATHER_API_RATE_LIMIT`: Requests per minute limit (default: 60)
- `GITHUB_WEBHOOK_SECRET`: GitHub webhook secret for signature validation (optional)
- `TLS_ENABLE`: Enable HTTPS (0 or 1, default: 0)

## Development

### Running migrations

```bash
docker compose exec app python manage.py makemigrations
docker compose exec app python manage.py migrate
```

### Creating superuser

```bash
docker compose exec app python manage.py createsuperuser
```

### Running Django shell

```bash
docker compose exec app python manage.py shell
```

### Accessing PostgreSQL

```bash
docker compose exec db psql -U postgres -d weather_forecast_db
```

## Testing

Run all BDD tests:

```bash
docker compose exec app python manage.py behave --no-input
```

Run specific feature:

```bash
docker compose exec app python manage.py behave --no-input features/005-rest-api.feature
```

Run with verbose output:

```bash
docker compose exec app python manage.py behave --no-input --verbose
```

## Known Limitations

1. **AsyncAPI Documentation**: WebSocket API lacks AsyncAPI specification documentation (only OpenAPI for REST endpoints is implemented)
2. **Third-party API Integration**: OpenWeatherMap integration uses mock data in test mode (api_key="test") and requires valid API key for production use
3. **Library Versions**: Project uses behave 1.2.6 (outdated, latest is 1.3.3) for compatibility with behave-django 1.4.0

## License

Educational project for demonstrating web API patterns.
