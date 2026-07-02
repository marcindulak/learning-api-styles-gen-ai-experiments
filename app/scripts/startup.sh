#!/bin/sh
# Container entrypoint: wait for the database, migrate, then serve the
# ASGI application with daphne, either over plain HTTP or over TLS.
#
# The protocol is controlled by the TLS_ENABLE environment variable.
# The value can be overridden at runtime by writing "0" or "1" to
# ${RUN_DIR}/tls_enable and killing the pid in ${RUN_DIR}/server.pid:
# the supervisor loop below restarts the server in the selected mode.
# The NFR-002 scenarios use this override to test both modes in one run.
set -e

cd /app

RUN_DIR=/tmp/wfs
mkdir -p "${RUN_DIR}"

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

terminate() {
    if [ -n "${server_pid:-}" ]; then
        kill "${server_pid}" 2>/dev/null || true
    fi
    exit 0
}
trap terminate TERM INT

set +e
while true; do
    if [ -f "${RUN_DIR}/tls_enable" ]; then
        tls_enable=$(cat "${RUN_DIR}/tls_enable")
    else
        tls_enable="${TLS_ENABLE:-0}"
    fi

    if [ "${tls_enable}" = "1" ]; then
        certs_dir="${APP_TLS_CERTS_DIR:-/etc/wfs/ssl/certs}"
        private_dir="${APP_TLS_PRICATE_DIR:-/etc/wfs/ssl/private}"
        certificate="${certs_dir}/wfs.crt"
        private_key="${private_dir}/wfs.key"
        if [ ! -f "${certificate}" ] || [ ! -f "${private_key}" ]; then
            echo "Generating a self-signed TLS certificate..." >&2
            openssl req -x509 -newkey rsa:2048 -nodes -days 365 \
                -keyout "${private_key}" -out "${certificate}" \
                -subj "/CN=localhost" \
                -addext "subjectAltName=DNS:localhost,DNS:django-app,IP:127.0.0.1"
        fi
        echo "Serving HTTPS on 0.0.0.0:${APP_PORT_HTTP:-8000} (TLS_ENABLE=${tls_enable})" >&2
        daphne -e "ssl:${APP_PORT_HTTP:-8000}:interface=0.0.0.0:privateKey=${private_key}:certKey=${certificate}" \
            config.asgi:application &
    else
        echo "Serving HTTP on 0.0.0.0:${APP_PORT_HTTP:-8000} (TLS_ENABLE=${tls_enable})" >&2
        daphne -b 0.0.0.0 -p "${APP_PORT_HTTP:-8000}" config.asgi:application &
    fi

    server_pid=$!
    echo "${server_pid}" > "${RUN_DIR}/server.pid"
    wait "${server_pid}"
    echo "Server process ${server_pid} exited, restarting..." >&2
    sleep 1
done
