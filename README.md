# Weather Forecast Service

A Django-based weather forecast service exposing weather data through multiple API styles: REST, GraphQL, Atom feeds, WebSockets, and webhooks. Built as an educational application to demonstrate various web API patterns in a single project.

## Tech Stack

- **Framework:** Django 5.1 with Django REST Framework
- **Database:** PostgreSQL 17
- **Cache/Channels:** Redis 7
- **GraphQL:** Strawberry GraphQL
- **WebSockets:** Django Channels with Daphne
- **Auth:** JWT (SimpleJWT)
- **Testing:** behave-django (BDD)
- **Containerization:** Docker Compose

## Prerequisites

- Docker and Docker Compose
- (Optional) Vagrant for VM-based development

## Getting Started

Build and start the services:

```bash
docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)
docker compose up --detach --wait
```

This starts three containers:
- **app** (Django) on `localhost:8000` (HTTP) and `localhost:8001` (WebSocket)
- **postgres** on `localhost:5432`
- **redis** on `localhost:6379`

The startup script automatically runs database migrations, creates an admin superuser (`admin`/`admin`), and seeds initial data.

## API Endpoints

All API routes are under `/api/`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/jwt/obtain` | POST | Obtain JWT access/refresh tokens |
| `/api/jwt/refresh` | POST | Refresh JWT access token |
| `/api/health` | GET | Health check |
| `/api/cities` | GET, POST | List/create cities |
| `/api/cities/<uuid>` | GET, PUT, PATCH, DELETE | City detail |
| `/api/cities/<uuid>/weather` | GET, POST | Weather records for a city |
| `/api/cities/<uuid>/forecast` | GET, POST | Forecasts for a city |
| `/api/alerts` | GET, POST | Weather alerts |
| `/api/graphql` | GET, POST | GraphQL endpoint |
| `/api/feed/forecasts` | GET | Atom feed of forecasts |
| `/api/webhooks/github` | POST | GitHub webhook receiver |
| `/admin/` | GET | Django admin interface |

### Authentication

Most write operations require a JWT token. Obtain one with:

```bash
curl -s -X POST http://localhost:8000/api/jwt/obtain \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin"}' | jq .access
```

Include the token in subsequent requests:

```bash
curl -H 'Authorization: Bearer <token>' http://localhost:8000/api/cities
```

### WebSocket

Weather alerts are broadcast over WebSocket at `ws://localhost:8001/ws/weather/alerts/`.

## Testing

Run BDD tests inside the Docker container:

```bash
docker compose exec app python manage.py behave --no-input
```

Test features cover:
- JWT authentication
- City CRUD operations
- Weather records and forecasts
- GitHub webhook integration

## Project Structure

```
app/
  config/          # Django settings, ASGI/WSGI, root URLs
  weather/         # Main application (models, views, serializers, schema, consumers)
  features/        # Behave BDD feature files and step definitions
  scripts/         # Startup and healthcheck scripts
compose.yaml       # Docker Compose service definitions
Dockerfile         # Application container image
requirements.txt   # Python dependencies
```

## License

MIT
