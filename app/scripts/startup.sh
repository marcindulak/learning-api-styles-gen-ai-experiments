#!/bin/sh
set -eu

# compose.yaml gates this container's start on postgres's own healthcheck
# (depends_on: condition: service_healthy), so postgres is already accepting
# connections by the time this script runs.
python manage.py migrate --no-input
python manage.py seed_cities
python manage.py seed_admin

# manage.py runserver has no option to also serve TLS, so daphne (already a
# direct dependency for Channels/WebSocket support) is invoked directly
# instead; it can bind an HTTP and an SSL endpoint from the same process.
set -- --endpoint "tcp:port=${APP_PORT_HTTP}:interface=0.0.0.0"
if [ "${TLS_ENABLE}" = "1" ]; then
    cert="${APP_TLS_CERTS_DIR}/self_signed.pem"
    key="${APP_TLS_PRIVATE_DIR}/self_signed.key"
    # The TLS cert/key directories are not bind-mounted, so they don't
    # survive a rebuild, but they do survive a plain container restart --
    # only regenerate when missing.
    if [ ! -f "${cert}" ] || [ ! -f "${key}" ]; then
        openssl req -x509 -newkey rsa:2048 -nodes -days 365 \
            -keyout "${key}" -out "${cert}" -subj "/CN=localhost"
    fi
    set -- "$@" --endpoint "ssl:port=${APP_PORT_HTTPS}:privateKey=${key}:certKey=${cert}:interface=0.0.0.0"
fi
exec python -m daphne "$@" config.asgi:application
