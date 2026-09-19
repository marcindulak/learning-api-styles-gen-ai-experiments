#!/usr/bin/env bash
# NFR-004 end-to-end test suite: exercises the running service exactly as
# REQUIREMENTS.md's own curl walkthrough does (obtain a JWT, create a city,
# find it by search_name, read it back by UUID), against a real running
# server rather than Django's test client. `--fail` makes curl itself exit
# non-zero on an HTTP error response, and `set -eu -o pipefail` propagates
# any curl/jq failure (including inside a pipeline) as this script's own
# non-zero exit status.
set -eu -o pipefail

BASE_URL="${E2E_BASE_URL:-http://localhost:8000}"
ADMIN_USERNAME="${ADMIN_USERNAME:-admin}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin}"
CITY_NAME="e2e-probe-city-$$"

CREDENTIALS_PAYLOAD=$(printf '{"username":"%s","password":"%s"}' "$ADMIN_USERNAME" "$ADMIN_PASSWORD")
ACCESS_TOKEN=$(curl --fail --silent \
  --data "$CREDENTIALS_PAYLOAD" \
  --header 'Content-Type: application/json' \
  --request POST \
  "$BASE_URL/api/jwt/obtain" | jq --raw-output '.access')

CREATE_CITY_PAYLOAD=$(printf '{"name":"%s","country":"Testland","region":"Test","timezone":"UTC","latitude":0.0,"longitude":0.0}' "$CITY_NAME")
curl --fail --silent \
  --data "$CREATE_CITY_PAYLOAD" \
  --header "Authorization: Bearer $ACCESS_TOKEN" \
  --header 'Content-Type: application/json' \
  --request POST \
  "$BASE_URL/api/cities" > /dev/null

CITY_UUID=$(curl --fail --silent \
  "$BASE_URL/api/cities?search_name=$CITY_NAME" | jq --raw-output '.results[0].uuid')

curl --fail --silent "$BASE_URL/api/cities/$CITY_UUID" \
  | jq --exit-status --arg name "$CITY_NAME" '.name == $name' > /dev/null

echo "e2e: obtained JWT, created and read back city '$CITY_NAME' ($CITY_UUID)"
