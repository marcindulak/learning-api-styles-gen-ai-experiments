#!/bin/bash

if [ "${TLS_ENABLE}" = "1" ]; then
    PROTOCOL="https"
    CURL_OPTS="--insecure"
else
    PROTOCOL="http"
    CURL_OPTS=""
fi

curl --fail --silent ${CURL_OPTS} "${PROTOCOL}://localhost:${APP_PORT_HTTP}/admin/login/" > /dev/null 2>&1
