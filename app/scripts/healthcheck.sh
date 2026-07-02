#!/bin/sh
# Container healthcheck: the API must answer on localhost over the
# protocol selected by TLS_ENABLE (or its runtime override, see
# scripts/startup.sh).
if [ -f /tmp/wfs/tls_enable ]; then
    tls_enable=$(cat /tmp/wfs/tls_enable)
else
    tls_enable="${TLS_ENABLE:-0}"
fi

if [ "${tls_enable}" = "1" ]; then
    curl --silent --fail \
        --cacert "${APP_TLS_CERTS_DIR:-/etc/wfs/ssl/certs}/wfs.crt" \
        "https://localhost:${APP_PORT_HTTP:-8000}/api/health"
else
    curl --silent --fail "http://localhost:${APP_PORT_HTTP:-8000}/api/health"
fi
