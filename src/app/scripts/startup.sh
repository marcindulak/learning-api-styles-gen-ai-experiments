#!/bin/bash
set -e

cd /app

echo "Running database migrations..."
python manage.py migrate --no-input

echo "Creating admin user if not exists..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@test.local', 'admin')
    print('Admin user created')
else:
    print('Admin user already exists')
"

echo "Starting Django application..."
python manage.py runserver 0.0.0.0:8000
