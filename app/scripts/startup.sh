#!/bin/sh
set -e

cd /app

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  sleep 1
done
echo "PostgreSQL is ready"

# Run migrations
python manage.py migrate --no-input

# Create superuser if it doesn't exist
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Admin user created')
else:
    print('Admin user already exists')
EOF

# Generate TLS certificates if enabled and not existing
if [ "$TLS_ENABLE" = "1" ]; then
    if [ ! -f "$APP_TLS_CERTS_DIR/cert.pem" ] || [ ! -f "$APP_TLS_PRICATE_DIR/key.pem" ]; then
        echo "Generating self-signed TLS certificate..."
        openssl req -x509 -newkey rsa:4096 -nodes \
            -keyout "$APP_TLS_PRICATE_DIR/key.pem" \
            -out "$APP_TLS_CERTS_DIR/cert.pem" \
            -days 365 -subj "/CN=localhost"
        echo "TLS certificate generated"
    fi
fi

# Start Daphne ASGI server
if [ "$TLS_ENABLE" = "1" ]; then
    echo "Starting Daphne with TLS on port 8443 and HTTP on port 8000..."
    daphne \
        --endpoint tcp:port=8000:interface=0.0.0.0 \
        --endpoint ssl:port=8443:privateKey=$APP_TLS_PRICATE_DIR/key.pem:certKey=$APP_TLS_CERTS_DIR/cert.pem \
        --verbosity 2 \
        config.asgi:application
else
    echo "Starting Daphne on port 8000..."
    daphne --bind 0.0.0.0 --port 8000 --verbosity 2 config.asgi:application
fi
