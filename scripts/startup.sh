#!/bin/bash
set -e

cd /app

# Wait for database to be ready
echo "Waiting for database..."
until python -c "import psycopg2; psycopg2.connect(host='db', port=5432, user='postgres', password='postgres', dbname='wfs')" 2>/dev/null; do
  sleep 1
done

echo "Database is ready"

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

# Start Django development server
echo "Starting Django server..."
python manage.py runserver 0.0.0.0:8000
