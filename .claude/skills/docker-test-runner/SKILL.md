# Docker Test Runner

**Triggers:** `docker test`, `run tests in docker`, `test in container`, `behave in docker`

**Multi-step workflow:** Build Docker image → Start services → Run tests → Report results → Stop services

---

## Overview

Runs the complete Weather Forecast Service test suite in Docker containers with PostgreSQL. Ensures tests run in the same environment as production (not local Python environment).

## When to Use

- After making code changes and need to verify they work
- Before committing changes (required by project workflow)
- Testing new feature implementations
- Running BDD scenarios (must be in Docker)
- Verifying database migrations and schema changes
- Testing API endpoints with real PostgreSQL database

## Steps

### Step 1: Check Prerequisites

Verify Docker and Docker Compose are available:
```bash
docker --version
docker compose --version
```

**If either is missing:** Install Docker Desktop or ensure Docker is installed on the system.

### Step 2: Build Docker Image (if needed)

Build or rebuild the Docker image with current UID/GID:
```bash
docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)
```

**When to rebuild:**
- After modifying `Dockerfile`
- After changing `requirements.txt` (Python dependencies)
- First time running the workflow
- If container exits with import errors

**Skip rebuilding** if no code/dependency changes since last build.

### Step 3: Start Services

Start PostgreSQL and Django services:
```bash
docker compose up --detach --wait
```

**Flags explained:**
- `--detach` — Services run in background
- `--wait` — Waits for health checks to pass (PostgreSQL ready, Gunicorn started)

**Verify services are healthy:**
```bash
docker compose ps
# Should show: app (running), postgres (running)
```

### Step 4: Run Tests

Choose the appropriate test command:

**Option A: BDD Tests (behave) — Required by REQUIREMENTS.md**
```bash
docker compose exec app python manage.py behave --no-input
```
Tests the application through user-facing scenarios.

**Option B: All Tests (unit + integration + BDD)**
```bash
docker compose exec app python manage.py test
```
Runs the complete test suite.

**Option C: Specific Test Module**
```bash
docker compose exec app python manage.py test tests.test_weather_rest -v 2
```
Tests a single module (REST API, GraphQL, etc.).

**Interpreting Output:**
- `OK` — All tests passed
- `FAILED` — Tests failed; read error messages to identify failures
- `ERROR` — Setup error (database migration, import error, etc.)

### Step 5: Check Logs (if tests fail)

If tests fail, inspect container logs:
```bash
docker compose logs app
```

Look for:
- Database connection errors
- Import errors (missing dependencies)
- API response mismatches
- Assertion failures

### Step 6: Stop Services

When done testing, stop services:
```bash
docker compose down
```

**If you need to reset the database (clean slate for next test run):**
```bash
docker compose down -v
```

The `-v` flag removes volumes, resetting the PostgreSQL database.

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| `Port already in use` | Service still running from previous session | `docker compose down` |
| `pg_isready not found` | `postgresql-client` not installed in image | Rebuild: `docker compose build` |
| `behave-django not found` | Wrong version in `requirements.txt` | Check `requirements.txt` has `behave-django>=1.9.0` |
| `connection refused (PostgreSQL)` | Database not ready | Wait longer, check `docker compose ps` health status |
| `test database does not exist` | Migrations haven't run | Startup script should run them; check logs |
| `GraphQL schema error` | Missing type annotations | Add `from strawberry.types import Info` to schema.py |

## Workflow Example

**Typical complete workflow:**

```bash
# Make code changes...

# Run the full test workflow
docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)
docker compose up --detach --wait
docker compose exec app python manage.py behave --no-input
# Tests pass ✓

# Stop services
docker compose down

# Commit changes
git add .
git commit -m "feature: add new API endpoint"
```

## Performance Notes

- **First build:** 2-5 minutes (downloads Python image, installs dependencies)
- **Subsequent builds:** 30 seconds (Docker caches layers)
- **Service startup:** 10-20 seconds (PostgreSQL initialization, Gunicorn startup)
- **BDD tests:** 30-60 seconds (depends on test count)
- **All tests:** 1-2 minutes (includes unit, integration, BDD)

## Key Files

- `Dockerfile` — Container image definition
- `compose.yaml` — Service orchestration (PostgreSQL + Django)
- `app/scripts/startup.sh` — Runs migrations, seeds data, starts Gunicorn + Daphne
- `requirements.txt` — Python dependencies
- `.claude/settings.json` — Docker command permissions

## Tips

- Use `docker compose logs app --follow` to watch logs in real-time while tests run
- Use `docker compose exec app bash` to get a shell inside the container for debugging
- Reset database between test runs with `docker compose down -v` for clean state
- Always use `--wait` flag in `docker compose up` to ensure services are ready before running tests
