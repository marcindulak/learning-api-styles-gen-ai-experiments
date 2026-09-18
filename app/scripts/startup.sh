#!/bin/sh
set -eu

# compose.yaml gates this container's start on postgres's own healthcheck
# (depends_on: condition: service_healthy), so postgres is already accepting
# connections by the time this script runs.
python manage.py migrate --no-input
python manage.py seed_cities
python manage.py seed_admin
exec python manage.py runserver "0.0.0.0:${APP_PORT_HTTP}"
