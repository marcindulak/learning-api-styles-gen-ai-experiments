# Weather Forecast Service

Educational application demonstrating various web API technologies in a single Django-based project. The Weather Forecast Service provides weather data for the 5 biggest cities in the world through multiple API interfaces.

## Features

### Web APIs
- **REST API** - Full CRUD operations with JWT authentication
- **GraphQL API** - Flexible query interface
- **WebSocket API** - Real-time weather alert notifications
- **GitHub Webhooks** - Event handling with HMAC signature verification
- **Atom Feed** - Syndication feed for weather forecasts

### Data Models
- Cities - Geographic locations with timezone information
- Weather Records - Current weather observations
- Weather Forecasts - Up to 7-day predictions
- Weather Alerts - Severe weather notifications
- Webhook Events - GitHub webhook event log

### Additional Features
- Django Admin CMS for data management
- OpenAPI 3.0 specification with Swagger UI and ReDoc
- AsyncAPI 3.0 specification for WebSocket documentation
- Comprehensive BDD tests with behave
- PostgreSQL database for data persistence
- Redis for WebSocket channel layers

## Technology Stack

- **Framework**: Django 6.0.2
- **Language**: Python 3.13
- **Database**: PostgreSQL 17
- **Cache/Channels**: Redis 7
- **ASGI Server**: Daphne
- **Containerization**: Docker & Docker Compose
- **Testing**: behave-django (BDD)

## Getting Started

### Prerequisites
- Docker
- Docker Compose

### Installation

1. Build the containers:
```bash
docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)
```

2. Start the services:
```bash
docker compose up --detach --wait
```

3. Verify all containers are healthy:
```bash
docker compose ps
```

The application will be available at:
- REST API: http://localhost:8000/api/
- GraphQL: http://localhost:8000/graphql
- Admin: http://localhost:8000/admin/
- API Docs: http://localhost:8000/api/docs

### Default Credentials

**Admin User**
- Username: `admin`
- Password: `admin`

## Usage

### REST API

#### Obtain JWT Token
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

#### Create a City
```bash
CREATE_CITY_PAYLOAD='{"name":"Copenhagen",
  "country":"Denmark",
  "region":"Europe",
  "timezone":"Europe/Copenhagen",
  "latitude":55.676100,
  "longitude":12.568300}'
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

#### List Cities
```bash
curl http://localhost:8000/api/cities | jq
```

#### Get City by UUID
```bash
CITY_UUID=$(docker compose exec app bash -c \
  "curl --request 'GET' --silent 'http://localhost:8000/api/cities?search_name=Copenhagen' | \
  jq --raw-output '.results[0].uuid'")
docker compose exec app bash -c \
       "curl \
       --request 'GET' \
       --silent \
       'http://localhost:8000/api/cities/$CITY_UUID' | \
       jq"
```

### GraphQL API

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{cities{name country region}}"}' | jq
```

### Atom Feed

```bash
curl http://localhost:8000/api/feeds/forecasts
```

### WebSocket API

Connect to `ws://localhost:8001/ws/alerts` to receive real-time weather alerts.

Example using websocat:
```bash
websocat ws://localhost:8001/ws/alerts
```

## API Documentation

### OpenAPI (REST API)
- **Schema**: http://localhost:8000/api/schema
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### AsyncAPI (WebSocket)
- **Specification**: `docs/asyncapi.yaml`

## Testing

### Run BDD Tests
```bash
docker compose exec app python manage.py behave --no-input
```

### Run Django Tests
```bash
docker compose exec app python manage.py test
```

## API Endpoints

### Authentication
- `POST /api/jwt/obtain` - Obtain JWT access and refresh tokens
- `POST /api/jwt/refresh` - Refresh access token

### Resources
- `/api/cities` - City management
- `/api/weather-records` - Current weather observations
- `/api/weather-forecasts` - Weather predictions
- `/api/weather-alerts` - Weather alert notifications

### WebSocket
- `/ws/alerts` - Real-time weather alert notifications

### Webhooks
- `POST /api/webhooks/github` - GitHub webhook handler

### Feeds
- `/api/feeds/forecasts` - Atom feed for weather forecasts

## Project Structure

```
.
├── app/
│   ├── config/              # Django settings and configuration
│   │   ├── asgi.py         # ASGI configuration
│   │   ├── postgres.py     # PostgreSQL settings
│   │   └── urls.py         # URL routing
│   ├── weather/            # Main application
│   │   ├── management/     # Django management commands
│   │   ├── migrations/     # Database migrations
│   │   ├── admin.py        # Admin interface configuration
│   │   ├── consumers.py    # WebSocket consumers
│   │   ├── feeds.py        # Atom feed
│   │   ├── models.py       # Data models
│   │   ├── routing.py      # WebSocket routing
│   │   ├── schema.py       # GraphQL schema
│   │   ├── serializers.py  # REST serializers
│   │   ├── views.py        # REST views
│   │   ├── weather_service.py  # Weather data generation
│   │   └── webhooks.py     # Webhook handlers
│   ├── features/           # BDD test features
│   │   ├── steps/          # Test step definitions
│   │   ├── authentication.feature
│   │   ├── cities.feature
│   │   └── environment.py
│   ├── scripts/            # Utility scripts
│   │   ├── startup.sh      # Container initialization
│   │   └── healthcheck.sh  # Health check script
│   └── manage.py           # Django management
├── docs/
│   └── asyncapi.yaml       # AsyncAPI specification
├── compose.yaml            # Docker Compose configuration
├── Dockerfile              # Container definition
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Environment Variables

### Database
- `POSTGRES_DB` - Database name (default: weather_forecast_service)
- `POSTGRES_USER` - Database user (default: postgres)
- `POSTGRES_PASSWORD` - Database password (default: postgres)
- `POSTGRES_HOST` - Database host (default: localhost)
- `POSTGRES_PORT` - Database port (default: 5432)

### Application
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (default: False)
- `APP_PORT_HTTP` - HTTP port (default: 8000)
- `TLS_ENABLE` - Enable TLS (default: 0)

### Redis
- `REDIS_HOST` - Redis host (default: redis)

### Webhooks
- `WEBHOOK_SECRET` - GitHub webhook secret

## Data Seeding

The 5 biggest cities are automatically seeded on startup:
1. Tokyo, Japan
2. Delhi, India
3. Shanghai, China
4. São Paulo, Brazil
5. Mumbai, India

Weather data can be generated using:
```bash
docker compose exec app python manage.py update_weather
```

## Development

### Access Django Shell
```bash
docker compose exec app python manage.py shell
```

### Create Migrations
```bash
docker compose exec app python manage.py makemigrations
```

### Apply Migrations
```bash
docker compose exec app python manage.py migrate
```

### Create Superuser
```bash
docker compose exec app python manage.py createsuperuser
```

## License

This is an educational project for demonstrating web API technologies.
