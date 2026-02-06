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

echo "Starting Django development server..."
python manage.py runserver 0.0.0.0:${APP_PORT_HTTP:-8000}
