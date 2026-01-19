#!/bin/bash
set -e

cd /app/app/app

echo "Running database migrations..."
python manage.py migrate

echo "Starting Django application..."
python manage.py runserver 0.0.0.0:8000
