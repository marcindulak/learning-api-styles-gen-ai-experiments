#!/bin/sh
# Container healthcheck used by HEALTHCHECK in the Dockerfile and by
# `docker compose up --wait`. The admin login page is served by Django's
# built-in admin app and does not require authentication, so it is a stable
# liveness probe even before any project-specific routes exist.
set -eu

exec curl --fail --silent --show-error \
    "http://localhost:${APP_PORT_HTTP:-8000}/admin/login/" >/dev/null
