#!/bin/bash
set -e

cd /app

# Wait for database to be ready
echo "Waiting for database..."
until python -c "import psycopg2; psycopg2.connect(host='db', port=5432, user='postgres', password='postgres', dbname='wfs')" 2>/dev/null; do
  sleep 1
done

echo "Database is ready"

# Generate self-signed TLS certificates if TLS is enabled and certificates don't exist
if [ "${TLS_ENABLE}" = "1" ]; then
  CERT_FILE="${APP_TLS_CERTS_DIR}/cert.pem"
  KEY_FILE="${APP_TLS_PRICATE_DIR}/key.pem"

  if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
    echo "Generating self-signed TLS certificates..."
    openssl req -x509 -newkey rsa:4096 -nodes \
      -keyout "$KEY_FILE" \
      -out "$CERT_FILE" \
      -days 365 \
      -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
    echo "TLS certificates generated"
  else
    echo "TLS certificates already exist"
  fi
fi

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

# Start Daphne ASGI server for WebSocket support
if [ "${TLS_ENABLE}" = "1" ]; then
  echo "Starting Daphne ASGI server with TLS support..."
  # Run Daphne with both HTTP and HTTPS endpoints
  daphne \
    --endpoint tcp:port=${APP_PORT_HTTP}:interface=0.0.0.0 \
    --endpoint ssl:port=8443:privateKey=${APP_TLS_PRICATE_DIR}/key.pem:certKey=${APP_TLS_CERTS_DIR}/cert.pem \
    src.wfs.asgi:application
else
  echo "Starting Daphne ASGI server (HTTP only)..."
  daphne --bind 0.0.0.0 --port "${APP_PORT_HTTP}" src.wfs.asgi:application
fi
