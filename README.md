# Weather Forecast Service

An educational Django application ("WFS") that exposes weather data through
several different web API styles side by side: REST, GraphQL, an Atom feed,
a WebSocket, and a GitHub webhook receiver, plus a content management system
built on Django's admin site.

See [REQUIREMENTS.md](REQUIREMENTS.md) for the requirements this project
implements and the reasoning behind its main technology choices, and
`features/*.feature` for the Gherkin specification each requirement is
implemented against.

## Running the service

The service is built and run with Docker Compose alone:

```
docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)
docker compose up --detach --wait
```

This also works unmodified inside a GitHub Codespace opened on this
repository (see `.devcontainer/devcontainer.json`).

Once running, the service is available at `http://localhost:8000` (and
`https://localhost:8443` with a self-signed certificate; see NFR-002). The
seeded admin credentials (`admin`/`admin` by default) are documented in
REQUIREMENTS.md's own curl walkthrough.

## API surfaces

| Style | Entry point |
|-------|-------------|
| REST | `/api/cities`, `/api/cities/{uuid}/current`, `/api/cities/{uuid}/history`, `/api/cities/{uuid}/forecast` |
| GraphQL | `POST /api/graphql` |
| Atom feed | `/api/cities/{uuid}/forecast/feed.atom` |
| WebSocket | `/ws/alerts/{uuid}/` |
| Webhook | `POST /api/webhooks/github` |
| CMS | `/admin/` (Django admin) |

Authentication uses JWT (`POST /api/jwt/obtain`); city reads are public,
writes and the WebSocket require a bearer token (see FR-010).

## API documentation

- OpenAPI (REST): `GET /api/schema`
- AsyncAPI (WebSocket alerts, GitHub webhook): `GET /api/async-schema`

## Testing

The integration test suite (`docker compose exec app python manage.py behave
--no-input`, per REQUIREMENTS.md) excludes scenarios tagged `@host-verified`:
these test the "app" container's own lifecycle (stopping/restarting it), so
they cannot run from a behave process launched inside that same container --
it would be killed by the very command it is testing. Those scenarios are
covered by standalone scripts instead, run directly on the host/CI runner:

```
docker compose up --detach --wait
tests/single_unit_lifecycle.sh
tests/clean_checkout_lifecycle.sh
tests/codespace_setup_lifecycle.sh
```

An end-to-end test against the live server (JWT, city CRUD) is also
available:

```
docker compose exec app tests/e2e.sh
```
