#!/bin/sh
# Container healthcheck: the HTTP API must answer on localhost.
curl --silent --fail "http://localhost:${APP_PORT_HTTP:-8000}/api/health"
