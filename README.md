# Weather Forecast Service

An educational Django application that exposes weather data over several web APIs
(REST, GraphQL, Atom feed, WebSocket, GitHub webhooks). It exists as a single
project so the APIs can be studied in a shared domain rather than as isolated
snippets.

The functional and non-functional requirements, together with the design
rationale, live in [REQUIREMENTS.md](REQUIREMENTS.md). The implementation is
driven from Gherkin feature files under [features/](features/); each file maps
to one requirement and carries a `@status-done` tag once its scenarios pass.

## Prerequisites

* [Docker](https://www.docker.com/) with Docker Compose v2.

## Build and run

```bash
docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)
docker compose up --detach --wait
```

The service listens on:

* `http://localhost:8000` — HTTP (REST, GraphQL, Atom, WebSocket at `/ws/alerts`).
* `https://localhost:8443` — HTTPS (same surface as port 8000).

TLS is enabled by default; set `TLS_ENABLE=0` in the environment of the `app`
service in `compose.yaml` to disable it.

## Run the test suite

The project uses [behave-django](https://behave-django.readthedocs.io/) for
end-to-end and integration tests against the running container:

```bash
docker compose exec app python manage.py behave --no-input
```

## End-to-end smoke test

Obtain a JWT access token and exercise the cities API:

```bash
CREDENTIALS_PAYLOAD='{"username":"admin","password":"admin"}'
ACCESS_TOKEN=$(docker compose exec app bash -c \
  "curl \
  --data '$CREDENTIALS_PAYLOAD' \
  --header 'Content-Type: application/json' \
  --request 'POST' \
  --silent 'http://localhost:8000/api/jwt/obtain' | \
  jq --raw-output '.access'")

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

## Project layout

* `src/` — Django application code (`cities`, `webhooks`, `config`, `scripts`).
* `features/` — Gherkin feature files and step definitions (one feature per
  requirement).
* `compose.yaml`, `Dockerfile` — container build and runtime.
* `REQUIREMENTS.md` — functional and non-functional requirements.
* `requirements.txt` — Python dependencies installed into the `app` image.

## License

Distributed under the terms of the [LICENSE](LICENSE) file.
