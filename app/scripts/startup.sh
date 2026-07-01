#!/bin/sh
# Container entrypoint: wait for the database, migrate, then serve HTTP.
set -e

cd /app

attempt=0
until python manage.py migrate --noinput; do
    attempt=$((attempt + 1))
    if [ "${attempt}" -ge 30 ]; then
        echo "Database is not ready after ${attempt} attempts, giving up." >&2
        exit 1
    fi
    echo "Database is not ready (attempt ${attempt}), retrying in 2s..." >&2
    sleep 2
done

exec python manage.py runserver "0.0.0.0:${APP_PORT_HTTP:-8000}"
