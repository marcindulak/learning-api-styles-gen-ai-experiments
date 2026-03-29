#!/bin/sh
set -e

APP_DIR="/app/app"

echo "==> Waiting for database..."
cd "$APP_DIR"
python manage.py migrate --no-input

echo "==> Collecting static files..."
python manage.py collectstatic --no-input --clear

echo "==> Creating admin superuser (if not exists)..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Admin user created.')
else:
    print('Admin user already exists.')
"

echo "==> Starting Daphne ASGI server on port 8000..."
if [ \"$TLS_ENABLE\" = \"1\" ]; then
    exec daphne \
        --bind 0.0.0.0 \
        --port 8000 \
        --ssl-certificate \"$APP_TLS_CERTS_DIR/cert.pem\" \
        --ssl-private-key \"$APP_TLS_PRICATE_DIR/key.pem\" \
        config.asgi:application
else
    exec daphne \
        --bind 0.0.0.0 \
        --port 8000 \
        config.asgi:application
fi
