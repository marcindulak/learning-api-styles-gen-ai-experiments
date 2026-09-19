#!/bin/sh
set -eu

curl --fail --silent --output /dev/null "http://localhost:${APP_PORT_HTTP}/admin/login/"
