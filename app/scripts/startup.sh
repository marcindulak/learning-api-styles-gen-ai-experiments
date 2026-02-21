#!/bin/bash
set -e

echo "Starting Weather Forecast Service..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
RETRIES=30
until pg_isready -h ${POSTGRES_HOST:-postgres} -p ${POSTGRES_PORT:-5432} -U ${POSTGRES_USER:-postgres} > /dev/null 2>&1 || [ $RETRIES -eq 0 ]; do
  echo "Waiting for PostgreSQL to start... $((RETRIES--)) attempts remaining"
  sleep 1
done

if [ $RETRIES -eq 0 ]; then
  echo "ERROR: PostgreSQL did not become ready in time"
  exit 1
fi

echo "PostgreSQL is ready!"

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create admin superuser if it doesn't exist
echo "Creating admin user..."
python manage.py shell <<EOF
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Admin user created')
else:
    print('Admin user already exists')
EOF

# Create regular user if it doesn't exist
echo "Creating regular user..."
python manage.py shell <<EOF
from django.contrib.auth.models import User
if not User.objects.filter(username='user').exists():
    User.objects.create_user('user', 'user@example.com', 'user')
    print('Regular user created')
else:
    print('Regular user already exists')
EOF

# TLS certificate generation (if enabled)
if [ "${TLS_ENABLE}" = "1" ]; then
    echo "TLS enabled - checking for certificates..."
    if [ ! -f "/etc/wfs/ssl/certs/server.crt" ] || [ ! -f "/etc/wfs/ssl/private/server.key" ]; then
        echo "Generating self-signed TLS certificates..."
        if [ -f "/app/scripts/generate_certs.sh" ]; then
            bash /app/scripts/generate_certs.sh
        else
            # Fallback inline cert generation
            openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
                -keyout /etc/wfs/ssl/private/server.key \
                -out /etc/wfs/ssl/certs/server.crt \
                -subj "/C=US/ST=State/L=City/O=WFS/CN=localhost"
        fi

        # Verify cert files exist
        if [ ! -f "/etc/wfs/ssl/certs/server.crt" ] || [ ! -f "/etc/wfs/ssl/private/server.key" ]; then
            echo "ERROR: Failed to generate TLS certificates"
            exit 1
        fi
        echo "TLS certificates generated successfully"
    else
        echo "TLS certificates already exist"
    fi
fi

# Signal handler to forward SIGTERM to child processes
cleanup() {
    echo "Received termination signal, shutting down..."
    if [ ! -z "$GUNICORN_PID" ]; then
        kill -TERM "$GUNICORN_PID" 2>/dev/null || true
    fi
    if [ ! -z "$DAPHNE_PID" ]; then
        kill -TERM "$DAPHNE_PID" 2>/dev/null || true
    fi
    wait
    exit 0
}

trap cleanup SIGTERM SIGINT

# Start Gunicorn (HTTP/HTTPS on port 8000)
echo "Starting Gunicorn on port 8000..."
if [ "${TLS_ENABLE}" = "1" ]; then
    gunicorn config.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 2 \
        --certfile=/etc/wfs/ssl/certs/server.crt \
        --keyfile=/etc/wfs/ssl/private/server.key \
        --access-logfile - \
        --error-logfile - &
else
    gunicorn config.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 2 \
        --access-logfile - \
        --error-logfile - &
fi
GUNICORN_PID=$!
echo "Gunicorn started with PID $GUNICORN_PID"

# Start Daphne (WebSocket on port 8001)
echo "Starting Daphne on port 8001..."
if [ "${TLS_ENABLE}" = "1" ]; then
    daphne config.asgi:application \
        --bind 0.0.0.0 \
        --port 8001 \
        --ssl-certificate /etc/wfs/ssl/certs/server.crt \
        --ssl-key /etc/wfs/ssl/private/server.key \
        --access-log - &
else
    daphne config.asgi:application \
        --bind 0.0.0.0 \
        --port 8001 \
        --access-log - &
fi
DAPHNE_PID=$!
echo "Daphne started with PID $DAPHNE_PID"

echo "Weather Forecast Service is running!"
echo "HTTP/HTTPS: port 8000 (Gunicorn PID: $GUNICORN_PID)"
echo "WebSocket: port 8001 (Daphne PID: $DAPHNE_PID)"

# Wait for either process to die
wait -n

# If we get here, one of the processes died
EXIT_CODE=$?
echo "ERROR: One of the server processes died (exit code: $EXIT_CODE)"
echo "Shutting down all processes..."
cleanup
exit $EXIT_CODE
