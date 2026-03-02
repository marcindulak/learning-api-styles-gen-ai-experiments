# Weather Forecast Service

A Django-based weather forecast service demonstrating multiple API paradigms: REST, GraphQL, Atom feeds, and WebSocket. Built using Behavior-Driven Development (BDD) with containerized deployment.

## Overview

The Weather Forecast Service (WFS) provides weather data for the 5 biggest cities in the world through various API interfaces. It integrates with third-party weather APIs, supports GitHub webhooks, provides real-time alerts, and includes an admin content management system.

## Features

- **Multiple API Paradigms**: REST, GraphQL, Atom feeds, WebSocket
- **Authentication**: JWT-based authentication with admin and regular user roles
- **Real-time Alerts**: WebSocket-based weather alerts with city subscriptions
- **Third-party Integration**: Fetch actual weather data from external APIs
- **GitHub Webhooks**: Trigger data refreshes via webhook events
- **Content Management**: Django admin interface for data management
- **API Documentation**: OpenAPI (Swagger), AsyncAPI, and GraphiQL interfaces
- **Security**: TLS/HTTPS support with dual HTTP/HTTPS endpoints
- **Containerized**: Docker Compose deployment with PostgreSQL database

## Requirements

- Docker and Docker Compose
- Git
- Port 8000 and 8443 available on localhost

## Quick Start

Build and start the services:

```bash
docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)
docker compose up --detach --wait
```

The service will be available at:
- HTTP: http://localhost:8000
- HTTPS: https://localhost:8443 (with self-signed certificate)

## Default Credentials

- **Admin user**: `admin` / `admin`
- **Database**: PostgreSQL on port 5432

## Running Tests

Execute the BDD test suite:

```bash
docker compose exec app behave --format progress
```

All 13 features with 55 scenarios should pass.

## API Endpoints

### REST API

Base URL: `http://localhost:8000/api`

**Authentication:**
```bash
curl --request POST \
  --header 'Content-Type: application/json' \
  --data '{"username":"admin","password":"admin"}' \
  http://localhost:8000/api/jwt/obtain
```

**Cities:**
- `GET /api/cities` - List all cities
- `GET /api/cities?search_name=Copenhagen` - Search cities by name
- `GET /api/cities/{uuid}` - Get specific city
- `POST /api/cities` - Create city (admin only)

**Weather Data:**
- `GET /api/weather/current` - List current weather for all cities
- `GET /api/weather/current/{city_name}` - Current weather for specific city
- `GET /api/weather/forecast/{city_name}` - 7-day forecast for specific city
- `GET /api/weather/historical?city={name}&start_date={date}&end_date={date}` - Historical data
- `POST /api/weather/current` - Store current weather (admin only)
- `POST /api/weather/forecast` - Store forecast (admin only)

**Admin Operations:**
- `POST /api/admin/fetch-weather` - Trigger third-party API fetch (admin only)

### GraphQL API

Endpoint: `http://localhost:8000/graphql`

Interactive GraphiQL interface available at the same URL in a browser.

**Example Query:**
```graphql
{
  currentWeather(cityName: "Copenhagen") {
    cityName
    temperature
    humidity
    pressure
    windSpeed
    conditions
  }
  forecast(cityName: "Copenhagen", days: 7) {
    forecastDate
    temperature
    conditions
  }
}
```

### Atom Feed

Endpoint: `http://localhost:8000/feeds/forecast/{city_name}/`

Subscribe to 7-day forecast feeds for specific cities in Atom format.

### WebSocket Alerts

Endpoint: `ws://localhost:8000/ws/alerts` or `wss://localhost:8443/ws/alerts`

**Connect and Subscribe:**
```json
{"type": "subscribe", "city": "Copenhagen"}
```

**Receive Alerts:**
```json
{
  "type": "alert",
  "city": "Copenhagen",
  "severity": "high",
  "message": "Strong winds expected",
  "timestamp": "2026-03-02T10:00:00Z"
}
```

**Unsubscribe:**
```json
{"type": "unsubscribe", "city": "Copenhagen"}
```

### GitHub Webhooks

Endpoint: `http://localhost:8000/webhooks/github`

Accepts GitHub push webhooks. Include `data-refresh` in commit message or ref to trigger weather data refresh for all cities.

Configure webhook secret via `GITHUB_WEBHOOK_SECRET` environment variable for signature validation.

### Admin Interface

URL: `http://localhost:8000/admin/`

Django admin interface for managing cities, weather data, alerts, and webhook events. Login with admin credentials.

## API Documentation

- **Swagger UI**: http://localhost:8000/api/docs/
- **OpenAPI Schema**: http://localhost:8000/api/schema/?format=json
- **GraphiQL**: http://localhost:8000/graphql
- **AsyncAPI Schema**: http://localhost:8000/api/asyncapi-schema/

## Project Structure

```
.
├── features/               # BDD feature files (Gherkin)
│   ├── 001_user_management.feature
│   ├── 002_city_management.feature
│   ├── ...
│   └── steps/             # Step definitions
├── src/
│   ├── weather/           # Django app with models, views, APIs
│   └── wfs/              # Django project settings
├── compose.yaml          # Docker Compose configuration
├── Dockerfile           # Container image definition
├── requirements.txt     # Python dependencies
└── REQUIREMENTS.md      # Project requirements specification
```

## Development

### Adding a City

```bash
ACCESS_TOKEN=$(docker compose exec app bash -c \
  "curl --silent --request POST \
  --header 'Content-Type: application/json' \
  --data '{\"username\":\"admin\",\"password\":\"admin\"}' \
  http://localhost:8000/api/jwt/obtain | jq --raw-output '.access'")

docker compose exec app bash -c \
  "curl --request POST \
  --header 'Authorization: Bearer $ACCESS_TOKEN' \
  --header 'Content-Type: application/json' \
  --data '{
    \"name\":\"Copenhagen\",
    \"country\":\"Denmark\",
    \"region\":\"Europe\",
    \"timezone\":\"Europe/Copenhagen\",
    \"latitude\":55.676100,
    \"longitude\":12.568300
  }' \
  http://localhost:8000/api/cities | jq"
```

### Fetching Weather Data

```bash
docker compose exec app bash -c \
  "curl --request POST \
  --header 'Authorization: Bearer $ACCESS_TOKEN' \
  --header 'Content-Type: application/json' \
  --data '{
    \"city_name\":\"Copenhagen\",
    \"data_type\":\"forecast\"
  }' \
  http://localhost:8000/api/admin/fetch-weather | jq"
```

## Testing Approach

This project uses Behavior-Driven Development (BDD) with:
- **Gherkin**: Feature specifications in `features/*.feature`
- **Behave**: Python BDD framework
- **End-to-end Tests**: HTTP requests via curl within container

Each feature file corresponds to a functional or non-functional requirement from REQUIREMENTS.md. Tests run against the actual Django server, validating the complete system.

## Technology Stack

- **Backend**: Django 5.1.5, Django REST Framework
- **Database**: PostgreSQL 17
- **ASGI Server**: Daphne (for WebSocket support)
- **GraphQL**: Graphene-Django
- **Authentication**: JWT (djangorestframework-simplejwt)
- **WebSocket**: Django Channels
- **Testing**: Behave, behave-django
- **Documentation**: drf-spectacular (OpenAPI)
- **Containerization**: Docker, Docker Compose

## Constraints

- Weather data limited to 5 cities
- Forecasts limited to 7 days from current date
- Monolithic deployment (single container for Django app)
- Self-signed TLS certificate for development

## Stopping the Service

```bash
docker compose down
```

Data persists in Docker volumes and will be available on next startup.

## License

This is an educational project demonstrating various web API paradigms and BDD practices.
