#!/bin/bash

# Health check script for Weather Forecast Service
# Checks both HTTP/HTTPS (port 8000) and WebSocket (port 8001)

# Allow initial startup time for cert generation
sleep 2

# Determine HTTP scheme based on TLS_ENABLE
if [ "${TLS_ENABLE}" = "1" ]; then
    SCHEME="https"
    CURL_OPTS="--insecure"
else
    SCHEME="http"
    CURL_OPTS=""
fi

# Check HTTP/HTTPS port 8000
if ! curl ${CURL_OPTS} --silent --fail --max-time 5 "${SCHEME}://localhost:8000/" > /dev/null 2>&1; then
    echo "ERROR: HTTP/HTTPS health check failed on port 8000"
    exit 1
fi

# Check WebSocket port 8001 is listening
if ! nc -zv localhost 8001 > /dev/null 2>&1; then
    echo "ERROR: WebSocket port 8001 not listening"
    exit 1
fi

# All checks passed
exit 0
