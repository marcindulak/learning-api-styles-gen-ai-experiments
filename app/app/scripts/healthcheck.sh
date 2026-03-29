#!/bin/sh
if [ "$TLS_ENABLE" = "1" ]; then
    curl --fail --silent --insecure https://localhost:8000/health/ || exit 1
else
    curl --fail --silent http://localhost:8000/health/ || exit 1
fi
