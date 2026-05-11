#!/bin/sh
# Container entrypoint: apply pending migrations, optionally start the TLS
# forwarder for NFR-002, then run Django's development server. Gunicorn or
# Daphne can replace runserver later when a production-grade NFR demands it.
set -eu

cd /app
python manage.py migrate --no-input

# NFR-002: when TLS is enabled, generate a self-signed certificate (idempotent;
# only when the files do not yet exist) and start a TLS-terminating forwarder
# that handles HTTPS on APP_PORT_HTTPS and proxies plain HTTP to runserver on
# APP_PORT_HTTP. The forwarder is backgrounded so runserver can stay PID 1
# and own the SIGTERM lifecycle that ``docker compose down`` relies on.
if [ "${TLS_ENABLE:-0}" = "1" ]; then
    cert_path="${APP_TLS_CERTS_DIR}/server.crt"
    key_path="${APP_TLS_PRICATE_DIR}/server.key"
    if [ ! -f "${cert_path}" ] || [ ! -f "${key_path}" ]; then
        openssl req \
            -x509 \
            -newkey rsa:2048 \
            -nodes \
            -days 365 \
            -keyout "${key_path}" \
            -out "${cert_path}" \
            -subj "/CN=localhost" \
            -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
    fi
    python /app/scripts/tls_forwarder.py \
        "${APP_PORT_HTTPS:-8443}" \
        "127.0.0.1" \
        "${APP_PORT_HTTP:-8000}" \
        "${cert_path}" \
        "${key_path}" &
fi

exec python manage.py runserver "0.0.0.0:${APP_PORT_HTTP:-8000}"
