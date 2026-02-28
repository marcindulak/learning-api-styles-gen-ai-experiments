#!/bin/bash
set -e

echo "=== Weather Forecast Service Startup ==="

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
until python -c "
import psycopg
conn = psycopg.connect(
    host='${POSTGRES_HOST:-postgres}',
    dbname='${POSTGRES_DB:-weather_forecast_service}',
    user='${POSTGRES_USER:-postgres}',
    password='${POSTGRES_PASSWORD:-postgres}',
)
conn.close()
" 2>/dev/null; do
    echo "PostgreSQL not ready, retrying in 2s..."
    sleep 2
done
echo "PostgreSQL is ready."

# Run migrations
echo "Running migrations..."
python manage.py migrate --no-input

# Create superuser if it doesn't exist
echo "Ensuring superuser exists..."
export DJANGO_SUPERUSER_USERNAME="${DJANGO_SUPERUSER_USERNAME:-admin}"
export DJANGO_SUPERUSER_PASSWORD="${DJANGO_SUPERUSER_PASSWORD:-admin}"
export DJANGO_SUPERUSER_EMAIL="${DJANGO_SUPERUSER_EMAIL:-admin@example.com}"
python manage.py createsuperuser --no-input 2>/dev/null || true

# Seed cities
echo "Seeding cities..."
python manage.py seed_cities

# Collect static files
python manage.py collectstatic --no-input 2>/dev/null || true

# Optional TLS
if [ "${TLS_ENABLE}" = "1" ]; then
    echo "Generating self-signed TLS certificate..."
    openssl req -x509 -newkey rsa:2048 -keyout "${APP_TLS_PRICATE_DIR}/key.pem" \
        -out "${APP_TLS_CERTS_DIR}/cert.pem" -days 365 -nodes \
        -subj "/CN=localhost" 2>/dev/null
    echo "TLS enabled."
fi

# Start Daphne (ASGI server handling both HTTP and WebSocket)
echo "Starting Daphne on ports 8000 (HTTP) and 8001 (WS)..."

# Start Django dev server on port 8000
python manage.py runserver 0.0.0.0:8000 &

# Start Daphne for WebSocket on port 8001
daphne -b 0.0.0.0 -p 8001 config.asgi:application

