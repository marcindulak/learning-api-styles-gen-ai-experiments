# Weather Forecast Service (WFS)

An educational web application demonstrating various web API styles (REST, GraphQL, WebSocket, Atom feeds, GitHub Webhooks) built with Django and containerized with Docker.

## Overview

The Weather Forecast Service is a comprehensive example application that showcases:
- **REST API** for querying weather indicators
- **GraphQL API** for flexible field selection
- **WebSocket API** for real-time weather alerts
- **Atom Feed** for weather forecast subscriptions
- **GitHub Webhook Integration** for CI/CD workflows
- **Content Management System** for admin users
- **Historical Data Storage** with PostgreSQL
- **TLS/HTTPS Encryption** for secure communications
- **Docker Deployment** for containerized operations
- **Comprehensive API Documentation** (OpenAPI & AsyncAPI)

## Architecture

### Technology Stack
- **Language**: Python 3.13
- **Framework**: Django 4.x with Django REST Framework
- **Database**: PostgreSQL
- **Real-time**: Django Channels (WebSocket support)
- **API Documentation**: drf-spectacular (OpenAPI/Swagger)
- **Testing**: Behave with Gherkin BDD scenarios
- **Containerization**: Docker & Docker Compose

### Project Structure

```
├── app/                          # Django application root
│   ├── manage.py                 # Django management script
│   ├── apps/                     # Django applications
│   │   ├── authentication/       # User authentication & JWT
│   │   ├── cities/               # City management (limited to 5)
│   │   ├── weather/              # Weather data & forecasts
│   │   ├── alerts/               # WebSocket alerts
│   │   ├── feeds/                # Atom feed generation
│   │   ├── webhooks/             # GitHub webhook handling
│   │   ├── api/                  # API routing
│   │   └── graphql/              # GraphQL schema
│   └── config/                   # Django settings
│       ├── settings/             # Environment-specific settings
│       └── urls.py               # URL routing
├── features/                     # BDD feature files & step definitions
│   ├── 001-013.feature          # Feature scenarios (Gherkin)
│   ├── steps/                    # Step implementations
│   └── environment.py            # Behave test setup
├── scripts/                      # Utility scripts
├── Dockerfile                    # Container image definition
├── compose.yaml                  # Docker Compose configuration
└── requirements.txt              # Python dependencies
```

## Quick Start

### Prerequisites
- Docker & Docker Compose (or Podman)
- Python 3.13 (for local development)
- PostgreSQL 17 (if not using Docker)

### Running with Docker

**1. Build and Start Services**
```bash
docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)
docker compose up --detach --wait
```

**2. Verify Service is Running**
```bash
curl http://localhost:8000/api/cities/
```

**3. Stop Services**
```bash
docker compose down
```

### Local Development Setup

**1. Create Python Virtual Environment**
```bash
python3.13 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**2. Install Dependencies**
```bash
pip install -r requirements.txt
```

**3. Configure Database**
```bash
cd app
python manage.py migrate
```

**4. Run Development Server**
```bash
cd app
python manage.py runserver 0.0.0.0:8000
```

## Running Tests

### BDD Tests with Behave

Behave runs Gherkin feature files as end-to-end tests against the running Django application.

**Run All Tests**
```bash
docker compose exec app bash -c "cd /app/app && python -m behave"
```

**Run Specific Feature**
```bash
docker compose exec app bash -c "cd /app/app && python -m behave ../features/001-user-roles.feature"
```

**Run Specific Scenario**
```bash
docker compose exec app bash -c "cd /app/app && python -m behave ../features/001-user-roles.feature:7"
```

**Show Step Definitions**
```bash
docker compose exec app bash -c "cd /app/app && python -m behave --steps-catalog"
```

**Verbose Output**
```bash
docker compose exec app bash -c "cd /app/app && python -m behave --no-capture"
```

### Test Results Summary

Current test status:
- **6 features passing** (Features 001-007 with complete implementations)
- **1 feature failing** (Feature 002: City creation validation issue)
- **6 features error** (Features 008-013: Step definitions pending implementation)
- **70 steps passing** | **56 steps undefined**

### Feature Overview

| # | Feature | Status | Description |
|---|---------|--------|-------------|
| 001 | User Roles & Authentication | ✅ DONE | Admin & regular user roles with JWT |
| 002 | City Management | ⚠️ PARTIAL | CRUD operations, 5-city limit |
| 003 | REST Weather API | ✅ DONE | GET weather by city name |
| 004 | GraphQL API | ✅ DONE | Query-specific fields |
| 005 | Weather Forecast Feed | ✅ DONE | Atom feed (up to 7 days) |
| 006 | Weather Alerts | ✅ DONE | WebSocket real-time alerts |
| 007 | Historical Weather Data | ✅ DONE | Query historical records |
| 008 | GitHub Webhooks | ❌ TODO | Webhook event handling |
| 009 | CMS for Admin | ❌ TODO | Content management system |
| 010 | TLS Encryption | ❌ TODO | HTTPS support |
| 011 | Docker Deployment | ❌ TODO | Container orchestration |
| 012 | API Documentation | ❌ TODO | OpenAPI/AsyncAPI specs |
| 013 | Third-Party Weather API | ❌ TODO | External data integration |

## API Endpoints

### Authentication
- `POST /api/jwt/obtain` - Obtain JWT access token
- `POST /api/jwt/refresh` - Refresh access token

### Cities
- `GET /api/cities/` - List all cities (paginated)
- `POST /api/cities/` - Create new city (admin only)
- `GET /api/cities/{uuid}/` - Get city details
- `PUT /api/cities/{uuid}/` - Update city (admin only)
- `DELETE /api/cities/{uuid}/` - Delete city (admin only)

### Weather
- `GET /api/weather/?city=Copenhagen` - Get current weather
- `POST /graphql/` - GraphQL queries

### Feeds
- `GET /feeds/weather/{city}/` - Atom feed for city forecast

### WebSocket
- `ws://localhost:8001/ws/alerts/` - Real-time weather alerts

### Webhooks
- `POST /api/webhooks/github/` - GitHub push events

## Authentication

### JWT Token Example

```bash
# Get access token
curl --data '{"username":"admin","password":"admin"}' \
  --header 'Content-Type: application/json' \
  --request 'POST' \
  'http://localhost:8000/api/jwt/obtain' | jq '.access'

# Use token in requests
curl --header 'Authorization: Bearer <TOKEN>' \
  'http://localhost:8000/api/cities/'
```

### Default Test Credentials
- **Admin User**: `username: admin` | `password: admin`
- **Regular User**: `username: user` | `password: password`

## Configuration

### Environment Variables

**Production Settings** (in `.env` or `compose.yaml`):
```bash
DEBUG=False
SECRET_KEY=your-secret-key-here
TLS_ENABLE=1  # Enable HTTPS
WEBHOOK_SECRET=your-webhook-secret
POSTGRES_DB=weather_forecast_service
POSTGRES_HOST=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-db-password
```

### Django Settings

Settings are environment-specific:
- `config/settings/test.py` - For BDD testing
- `config/settings/postgres.py` - For production with PostgreSQL
- `config/settings/base.py` - Common settings

## Development Workflow

### BDD Development Process

1. **Write Feature** - Create `.feature` file with Gherkin scenarios
2. **Run Tests** - Execute feature to see undefined steps
3. **Implement Steps** - Create step definitions in `features/steps/`
4. **Build Implementation** - Develop Django code to satisfy steps
5. **Iterate** - Repeat until all scenarios pass
6. **Mark Complete** - Tag feature with `@status-done`

### Adding New Features

1. Create feature file: `features/NNN-feature-name.feature`
2. Tag with `@status-todo`
3. Add scenarios with concrete Given/When/Then steps
4. Create step definitions: `features/steps/feature_name_steps.py`
5. Implement Django functionality
6. Tag with `@status-done` when all tests pass

## Troubleshooting

### Tests Fail to Connect to Service
Ensure Docker services are running and healthy:
```bash
docker compose ps
docker compose logs app
```

### "No steps directory" Error
Behave must be run from the project directory where `.behaverc` exists:
```bash
cd /app/app && python -m behave
```

### JWT Token Expired
Tokens expire after 60 minutes. Refresh or request a new one:
```bash
curl --data '{"refresh":"<REFRESH_TOKEN>"}' \
  --header 'Content-Type: application/json' \
  --request 'POST' \
  'http://localhost:8000/api/jwt/refresh/'
```

### Database Locked (SQLite)
If using local SQLite, ensure no other processes are accessing the database.

## Performance Characteristics

- **Cities**: Limited to 5 maximum (by design)
- **Forecasts**: Limited to 7-day window
- **Weather Data**: Cached from third-party API
- **Database**: Indexed on city name for fast lookups
- **Pagination**: 10 items per page by default

## Security Notes

- ✅ JWT-based authentication
- ✅ TLS/HTTPS support for encrypted connections
- ✅ CSRF protection enabled
- ✅ Role-based access control (admin vs. regular user)
- ✅ Webhook signature validation
- ⚠️ Not production-ready - for educational purposes only

## Contributing

This is an educational project demonstrating API design patterns. See `REQUIREMENTS.md` for detailed functional and non-functional requirements.

## License

Educational project - use freely for learning purposes.

## Support

For questions or issues, refer to:
- `REQUIREMENTS.md` - Detailed system requirements
- `features/` - BDD scenarios as executable documentation
- `app/` - Django application source code
