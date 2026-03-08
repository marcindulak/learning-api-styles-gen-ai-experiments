#!/bin/sh
curl --fail --silent http://localhost:8000/admin/ >/dev/null || exit 1
