#!/bin/sh
# Container entrypoint: apply pending migrations, then run Django's
# development server. Gunicorn/Daphne can replace runserver later when a
# production-grade NFR (e.g. NFR-002) demands it.
set -eu

cd /app
python manage.py migrate --no-input
exec python manage.py runserver "0.0.0.0:${APP_PORT_HTTP:-8000}"
