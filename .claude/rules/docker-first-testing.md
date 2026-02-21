# Docker-First Testing Workflow

All tests run in Docker containers with PostgreSQL. Local development without containers is unsupported.

## The Requirement

**BDD tests MUST run in Docker Compose, not locally.** This ensures the test environment matches production exactly (PostgreSQL version, Python version, all dependencies in Docker image).

## The Pattern

**Setup (one-time):**

```bash
# Build Docker image with current UID/GID (preserves file permissions)
docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)

# Start services (PostgreSQL + Gunicorn + Daphne)
docker compose up --detach --wait

# Verify services are healthy
docker compose ps
```

**Running Tests:**

```bash
# BDD tests (behave) — REQUIRED by REQUIREMENTS.md
docker compose exec app python manage.py behave --no-input

# All tests (unit + integration + BDD)
docker compose exec app python manage.py test

# Specific test module
docker compose exec app python manage.py test tests.test_weather_rest -v 2
```

**Stopping:**

```bash
# Stop all services
docker compose down

# Stop and remove volumes (reset database)
docker compose down -v

# View logs while running
docker compose logs app
```

## Why This Pattern

- **Environment Parity:** Container environment == production environment
- **Database Isolation:** Each test run starts with clean PostgreSQL 17 database
- **Consistent Dependencies:** All Python packages installed in Docker, version-locked in `requirements.txt`
- **Integration Testing:** Tests verify actual database operations, not mocks
- **CI/CD Ready:** Same container runs locally and in CI pipelines

## Common Mistakes

- **Running tests locally without Docker** — Won't work; PostgreSQL must be running in container
- **Not using `--wait` flag** — Services start asynchronously; `docker compose up --wait` ensures PostgreSQL is healthy before tests run
- **Forgetting to build after code changes** — Must `docker compose build` after modifying Dockerfile or `requirements.txt`
- **Tests passing locally, failing in Docker** — Usually version mismatch (Python, PostgreSQL, package versions differ)
- **Not resetting database between test runs** — Use `docker compose down -v` to remove volumes and reset

## Setup Checklist

- [ ] Docker and Docker Compose installed
- [ ] `.claude/settings.json` allows docker commands (both user + project level)
- [ ] `Dockerfile` exists with `ENTRYPOINT` pointing to startup script
- [ ] `compose.yaml` defines both `app` and `postgres` services
- [ ] `app/scripts/startup.sh` runs migrations and starts Gunicorn + Daphne
- [ ] `requirements.txt` contains all dependencies
- [ ] Health checks configured (PostgreSQL: `pg_isready -U postgres`, app: http health endpoint)
- [ ] `--wait` flag used in `docker compose up` command

## Container Services

**PostgreSQL 17 (port 5432):**
- Database: `weather_forecast_service`
- User: `postgres` (password: `postgres`)
- Health check: `pg_isready -U postgres`

**Django App (port 8000 HTTP, 8001 WebSocket):**
- Gunicorn serves REST, GraphQL, Swagger UI
- Daphne serves WebSocket
- Health check: `curl http://localhost:8000/api/docs/`

## Permissions

Docker commands must be allowed in `.claude/settings.json`:

**User-level (`~/.claude/settings.json`):**
```json
"allow": [
  "Bash(docker:*)",
  "Bash(docker compose build:*)",
  "Bash(docker compose up:*)",
  "Bash(docker compose down:*)",
  "Bash(docker compose exec:*)"
]
```

**Project-level (`/vagrant/.claude/settings.json`):**
```json
"allow": [
  "Bash(docker:*)",
  "Bash(docker compose build:*)",
  "Bash(docker compose up:*)",
  "Bash(docker compose down:*)",
  "Bash(docker compose exec:*)"
]
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| **Port already in use** | `docker compose down`, check `lsof -i :8000` |
| **PostgreSQL healthcheck fails** | Ensure `pg_isready -U postgres` in healthcheck (with -U postgres) |
| **pg_isready command not found** | Add `postgresql-client` to Dockerfile apt-get install |
| **behave-django version conflict** | Use `behave-django>=1.9.0`, not `>=2.0.0` (v2 doesn't exist) |
| **GraphQL schema errors** | Add `from strawberry.types import Info` and type all `info` parameters |
| **WebSocket connect fails** | Ensure Daphne running on port 8001; check `docker compose logs app` |

## Key Files

- `Dockerfile` — Container image definition with Python, dependencies, startup script
- `compose.yaml` — Services definition (PostgreSQL + Django), environment variables, ports
- `requirements.txt` — Python dependencies (must match Dockerfile expectations)
- `app/scripts/startup.sh` — Entry point (migrations, seed data, start Gunicorn + Daphne)
- `app/scripts/healthcheck.sh` — Health check script for Docker health status
- `.claude/settings.json` — Permission configuration for Docker commands
