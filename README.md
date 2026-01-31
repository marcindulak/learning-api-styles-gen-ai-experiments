# Weather Forecast Service

A Django-based weather forecast application that exposes weather data through multiple API styles including REST, GraphQL, Atom feeds, and WebSockets.

## Features

| Feature | Description |
|---------|-------------|
| JWT Authentication | Secure API access using JSON Web Tokens |
| City Management | CRUD operations for cities (limited to 5 biggest cities) |
| Weather Forecast | Up to 7-day weather forecasts with common indicators |
| Historical Data | Access past weather records by date |
| User Roles | Admin and regular user permissions |
| REST API | Weather indicators via RESTful endpoints |
| GraphQL API | Flexible weather data queries |
| GitHub Webhooks | Integration for repository event notifications |
| Atom Feed | Subscribe to weather forecasts via feed readers |
| WebSocket Alerts | Real-time severe weather notifications |

## Tech Stack

- **Framework**: Django
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **Containerization**: Docker
- **Testing**: django-behave (BDD)

## Quick Start

Build and start the containers:

```bash
docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)
docker compose up --detach --wait
```

Run the test suite:

```bash
docker compose exec app python manage.py behave --no-input
```

## API Usage

### Obtain JWT Token

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

### Create a City

```bash
CREATE_CITY_PAYLOAD='{"name":"Tokyo",
  "country":"Japan",
  "region":"Asia",
  "timezone":"Asia/Tokyo",
  "latitude":35.689500,
  "longitude":139.691700}'
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

### Get City by UUID

```bash
CITY_UUID=$(docker compose exec app bash -c \
  "curl --request 'GET' --silent 'http://localhost:8000/api/cities?search_name=Tokyo' | \
  jq --raw-output '.results[0].uuid'")
docker compose exec app bash -c \
  "curl \
  --request 'GET' \
  --silent \
  'http://localhost:8000/api/cities/$CITY_UUID' | \
  jq"
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/jwt/obtain` | POST | Obtain JWT access token |
| `/api/cities` | GET, POST | List/create cities |
| `/api/cities/{uuid}` | GET, PUT, DELETE | City operations |
| `/api/cities/{uuid}/forecast` | GET | Weather forecast |
| `/api/cities/{uuid}/weather` | GET | Current weather |
| `/api/cities/{uuid}/historical` | GET | Historical weather data |
| `/api/graphql` | POST | GraphQL endpoint |
| `/api/webhooks/github` | POST | GitHub webhook receiver |
| `/feeds/{uuid}/feed.atom` | GET | Atom feed for city |
| `/ws/alerts/{uuid}/` | WebSocket | Real-time weather alerts |

## Weather Indicators

The service provides the following weather data:

- Temperature (Celsius)
- Humidity (percentage)
- Wind speed (meters per second)
- Atmospheric pressure
- Weather condition code and description

## Constraints

- Maximum of 5 cities in the system
- Weather forecasts limited to 7 days
- Admin users can create, update, and delete cities
- Regular users have read-only access to weather data
