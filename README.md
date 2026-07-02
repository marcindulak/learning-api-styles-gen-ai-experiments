# Weather Forecast Service

An educational Django application that encapsulates various web APIs into
one project: REST, GraphQL, Atom, webhooks, and WebSockets, backed by
PostgreSQL and Redis. See [REQUIREMENTS.md](REQUIREMENTS.md) for the full
list of functional and non-functional requirements.

## Prerequisites

The only requirement on the host is [Docker](https://www.docker.com/) with
the Compose plugin. No language toolchain needs to be installed: everything
runs in containers.

## Quick start

Build and start the whole service stack from the repository root:

```
docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)
docker compose up --detach --wait
```

The service is then available at http://localhost:8000 — verify with:

```
curl http://localhost:8000/api/health
```

To stop the stack:

```
docker compose down
```

### Encrypted (TLS) mode

By default the service speaks plain HTTP. To serve HTTPS with a generated
self-signed certificate instead, start the stack with `TLS_ENABLE=1`:

```
TLS_ENABLE=1 docker compose up --detach --wait
```

## Seed data

Weather data collection is limited to the 5 biggest cities in the world.
Create them, then fetch real weather and forecast data from the third-party
weather API ([Open-Meteo](https://open-meteo.com/)):

```
docker compose exec app python manage.py seed_cities
docker compose exec app python manage.py fetch_weather --all
docker compose exec app python manage.py fetch_forecast Tokyo
```

An admin user for the CMS and the writable APIs is created with:

```
docker compose exec app python manage.py createsuperuser
```

## APIs

| Endpoint | Description |
|----------|-------------|
| `/api/health` | Health check |
| `/api/jwt/obtain` | Obtain a JWT access token |
| `/api/cities` | Cities collection (REST) |
| `/api/cities/<uuid>` | City detail (REST) |
| `/api/cities/<uuid>/weather` | Current weather for a city |
| `/api/cities/<uuid>/weather/history` | Historical weather (`start`/`end` dates) |
| `/api/cities/<uuid>/forecast` | Forecast, up to 7 days (`days` parameter) |
| `/api/cities/<uuid>/forecast/feed` | Forecast feed (Atom) |
| `/graphql` | GraphQL endpoint with GraphiQL UI |
| `/ws/alerts` | Weather alerts (WebSocket) |
| `/api/webhooks/github` | GitHub webhook receiver |
| `/api/schema` | OpenAPI specification |
| `/api/docs` | Interactive API documentation (Swagger UI) |
| `/api/asyncapi` | AsyncAPI specification |
| `/admin/` | Content management system (admin user) |

## Tests

The Gherkin feature suite in [features/](features/) runs inside the app
container with behave-django:

```
docker compose exec app python manage.py behave --no-input
```

## GitHub Codespaces

The repository ships a [devcontainer definition](.devcontainer/devcontainer.json)
so it can be opened directly in GitHub Codespaces (or any dev-container
tool): the compose stack is started automatically and ports 8000/8001 are
forwarded.
