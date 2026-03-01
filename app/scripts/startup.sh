#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
until pg_isready -h "${POSTGRES_HOST}" -U "${POSTGRES_USER}"; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done
echo "PostgreSQL is up"

echo "Running migrations..."
python manage.py migrate --no-input

echo "Creating superuser if it doesn't exist..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Superuser created: username=admin, password=admin')
else:
    print('Superuser already exists')
EOF

echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

if [ "${TLS_ENABLE}" = "1" ]; then
    echo "Generating self-signed TLS certificates..."
    if [ ! -f "${APP_TLS_PRICATE_DIR}/key.pem" ] || [ ! -f "${APP_TLS_CERTS_DIR}/cert.pem" ]; then
        openssl req -x509 -newkey rsa:4096 -keyout "${APP_TLS_PRICATE_DIR}/key.pem" -out "${APP_TLS_CERTS_DIR}/cert.pem" -days 365 -nodes -subj "/CN=localhost"
        echo "TLS certificates generated"
    else
        echo "TLS certificates already exist"
    fi
    echo "Starting Django with TLS on port ${APP_PORT_HTTP}..."
    exec daphne -b 0.0.0.0 -e ssl:${APP_PORT_HTTP}:privateKey=${APP_TLS_PRICATE_DIR}/key.pem:certKey=${APP_TLS_CERTS_DIR}/cert.pem config.asgi:application
else
    echo "Starting Django without TLS..."
    exec daphne -b 0.0.0.0 -p ${APP_PORT_HTTP} config.asgi:application
fi
