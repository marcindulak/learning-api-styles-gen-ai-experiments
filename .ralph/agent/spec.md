# Run Behave Tests in Docker — Specification

## Summary

Enable Docker command permissions in `.claude/settings.json` and run the existing behave-django BDD test suite inside the Docker containerized environment.

---

## Pre-conditions

- `.claude/settings.json` must allow `Bash(docker *)` and `Bash(docker compose *)` commands (moved from `deny` to `allow` list).
- Docker and Docker Compose must be available on the host.

## Acceptance Criteria

### AC-1: Docker permissions enabled

- **Given** the `.claude/settings.json` file
- **When** reviewed
- **Then** `Bash(docker *)` and `Bash(docker compose *)` are in the `permissions.allow` array
- **And** `Bash(docker *)` is NOT in the `permissions.deny` array

### AC-2: Docker containers build and start successfully

- **Given** the project's `compose.yaml` and `Dockerfile`
- **When** running `docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)`
- **Then** the image builds without errors
- **When** running `docker compose up --detach --wait`
- **Then** all three services (app, postgres, redis) are healthy
- **And** `docker compose ps` shows all containers in "running" state with healthy status

### AC-3: Behave tests execute inside the Docker container

- **Given** all containers are running and healthy
- **When** running `docker compose exec app python manage.py behave --no-input`
- **Then** the behave test suite executes against the Dockerized Django app with PostgreSQL backend
- **And** test output shows results for all feature files:
  - `features/authentication.feature` — JWT authentication scenarios
  - `features/cities.feature` — City CRUD operations
  - `features/weather.feature` — Weather records and forecasts
  - `features/webhooks.feature` — GitHub webhook integration

### AC-4: All tests pass

- **Given** behave tests have executed
- **When** the test run completes
- **Then** all scenarios pass (exit code 0)
- **And** no failures or errors are reported

---

## Edge Cases & Error Conditions

| Scenario | Expected Behavior |
|----------|-------------------|
| Docker daemon not running | `docker compose build` fails with clear error; do not proceed |
| Container fails healthcheck | `docker compose up --wait` exits non-zero; investigate logs |
| Database migrations fail | `startup.sh` should have run migrations; check `docker compose logs app` |
| Behave test failures | Report which scenarios failed with full output for debugging |

---

## Out of Scope

- Writing new behave tests — only running existing ones
- Modifying the Docker configuration (Dockerfile, compose.yaml)
- Running tests outside of Docker (local/host execution)
- CI/CD pipeline configuration
