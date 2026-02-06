#!/bin/bash

curl -f http://localhost:${APP_PORT_HTTP:-8000}/ || exit 1
