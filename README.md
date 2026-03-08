# Weather Forecast Service

A Django-based educational weather forecast service demonstrating various web API patterns and technologies.

## Project Overview

The Weather Forecast Service (WFS) provides weather data for the 5 biggest cities in the world through multiple API formats:

- REST API with JWT authentication
- GraphQL API with selective field queries
- Atom feeds for forecast data
- WebSocket connections for real-time weather alerts
- GitHub webhook integration for automated data updates

## Features

- **User Management**: JWT-based authentication with admin and regular user roles
- **City Management**: CRUD operations for city data (admin-only writes, public reads)
- **Weather Data Storage**: Current weather, 7-day forecasts, and historical data
- **Multiple API Formats**: REST, GraphQL, Atom feeds, WebSocket
- **Third-Party API Integration**: Weather data fetching with mock support for testing
- **Admin Interface**: Django admin for content management
- **API Documentation**: OpenAPI/Swagger UI, GraphiQL, AsyncAPI specs
- **Security**: TLS support with self-signed certificates
- **Containerized Deployment**: Docker Compose setup with PostgreSQL

## Technology Stack

- Python 3.13
- Django 5.1
- Django REST Framework
- Django Channels with Daphne ASGI server
- GraphQL (graphene-django)
- PostgreSQL
- Docker & Docker Compose

## Prerequisites

- Docker
- Docker Compose
- Git

## Setup

Build and start the containers:

```bash
docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)
docker compose up --detach --wait
```

The service will be available at:
- HTTP: http://localhost:8000
- HTTPS: https://localhost:8443 (self-signed certificate)

## Running Tests

Run the BDD test suite using Behave:

```bash
docker compose exec app python -m behave features/ --no-capture --format progress
```

Expected output: 13 features, 55 scenarios, 214 steps passing.

## API Endpoints

### Authentication

Obtain JWT access token:

```bash
docker compose exec app bash -c "curl --request POST --header 'Content-Type: application/json' --data '{\"username\":\"admin\",\"password\":\"admin\"}' --silent http://localhost:8000/api/jwt/obtain/ | jq"
```

### REST API

Create a city (admin only):

```bash
ACCESS_TOKEN="your_token_here"
docker compose exec app bash -c "curl --request POST --header 'Authorization: Bearer $ACCESS_TOKEN' --header 'Content-Type: application/json' --data '{\"name\":\"Copenhagen\",\"country\":\"Denmark\",\"region\":\"Europe\",\"timezone\":\"Europe/Copenhagen\",\"latitude\":55.6761,\"longitude\":12.5683}' --silent http://localhost:8000/api/cities/ | jq"
```

List cities (public):

```bash
docker compose exec app bash -c "curl --request GET --silent http://localhost:8000/api/cities/ | jq"
```

Get current weather by city name (public):

```bash
docker compose exec app bash -c "curl --request GET --silent http://localhost:8000/api/weather/current/Copenhagen/ | jq"
```

### GraphQL API

Query weather data with selective fields:

```bash
docker compose exec app bash -c "curl --request POST --header 'Content-Type: application/json' --data '{\"query\":\"{ currentWeather(cityName: \\\"Copenhagen\\\") { temperature humidity } }\"}' --silent http://localhost:8000/graphql | jq"
```

Access GraphiQL interface: http://localhost:8000/graphql

### Atom Feed

Get forecast feed for a city:

```bash
docker compose exec app bash -c "curl --request GET --silent http://localhost:8000/feeds/forecast/Copenhagen/"
```

### WebSocket API

Connect to weather alerts (requires WebSocket client):

```
ws://localhost:8000/ws/alerts/
```

Subscribe to city alerts:

```json
{"action": "subscribe", "city": "Copenhagen"}
```

### Admin Interface

Access Django admin: http://localhost:8000/admin/

Default credentials:
- Username: `admin`
- Password: `admin`

### API Documentation

- OpenAPI schema: http://localhost:8000/api/schema/
- Swagger UI: http://localhost:8000/api/schema/swagger-ui/
- AsyncAPI schema: http://localhost:8000/api/asyncapi/

## Architecture

The project follows a Django monolithic architecture:

```
app/
├── config/           # Django project settings
│   ├── asgi.py      # ASGI config for Channels/WebSocket
│   ├── settings.py  # Django settings
│   └── urls.py      # URL routing
├── weather/         # Main Django app
│   ├── models.py    # Data models (City, Weather, Alerts, etc.)
│   ├── serializers.py # DRF serializers
│   ├── views.py     # API views and viewsets
│   ├── schema.py    # GraphQL schema
│   ├── consumers.py # WebSocket consumers
│   ├── feeds.py     # Atom feed generators
│   └── admin.py     # Admin interface config
├── features/        # BDD test scenarios (Gherkin)
│   └── steps/       # Step definitions
└── manage.py        # Django management command
```

## Database

PostgreSQL database runs in a separate container. Connection details:

- Host: `db`
- Port: `5432`
- Database: `weather_db`
- User: `weather_user`
- Password: `weather_password`

## Development

The container has no volume mount for the application code. To apply code changes:

1. Make changes to local files
2. Copy files to container: `docker compose cp app/file.py app:/app/file.py`
3. Restart container: `docker compose restart app`

Or rebuild completely: `docker compose down && docker compose build --no-cache && docker compose up --detach --wait`

## Testing Approach

The project uses Behavior-Driven Development (BDD) with Gherkin feature files:

- Feature files define scenarios with Given/When/Then steps
- Step definitions use subprocess curl commands to test HTTP endpoints
- Tests run inside the container against the running Django server
- All scenarios must pass before marking features as complete

## Security Notes

- TLS certificates are self-signed (for development only)
- Default admin credentials should be changed in production
- GitHub webhook secret should be configured via `GITHUB_WEBHOOK_SECRET` environment variable
- CSRF protection is disabled for webhook endpoints only

## License

Educational project for demonstrating web API patterns.
