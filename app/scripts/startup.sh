#!/bin/bash
set -e

echo "Starting Weather Forecast Service..."

cd /app

echo "Waiting for database..."
until python -c "import psycopg; psycopg.connect('postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}/${POSTGRES_DB}').close()" 2>/dev/null; do
  echo "Database not ready, waiting..."
  sleep 1
done
echo "Database ready!"

if [ "${TLS_ENABLE:-0}" = "1" ]; then
    echo "TLS enabled, installing django-sslserver..."
    python -m pip install --quiet django-sslserver==0.22
fi

echo "Running database migrations..."
python manage.py migrate --no-input

echo "Creating superuser if it doesn't exist..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Superuser created: admin/admin')
else:
    print('Superuser already exists')
EOF

if [ "${TLS_ENABLE:-0}" = "1" ]; then
    echo "TLS enabled, generating self-signed certificates..."
    CERT_FILE="${APP_TLS_CERTS_DIR}/server.crt"
    KEY_FILE="${APP_TLS_PRICATE_DIR}/server.key"

    if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
        openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost" \
            -keyout "$KEY_FILE" \
            -out "$CERT_FILE"
        echo "Self-signed certificate generated"
    else
        echo "Using existing certificates"
    fi

    echo "Starting Django HTTPS server on port 8443..."
    python manage.py runsslserver 0.0.0.0:8443 --certificate "$CERT_FILE" --key "$KEY_FILE"
else
    echo "Starting Django HTTP server on port ${APP_PORT_HTTP:-8000}..."
    python manage.py runserver 0.0.0.0:${APP_PORT_HTTP:-8000}
fi
