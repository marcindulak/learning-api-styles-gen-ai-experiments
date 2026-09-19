#!/usr/bin/env bash
# NFR-003 Scenario 2: "The application starts and stops as a single unit".
#
# This must run from wherever `docker compose` itself is invoked (the host or
# CI runner), never from inside the "app" container via the project's normal
# `docker compose exec app python manage.py behave` command: stopping app
# would kill that very process before it could observe the fact it is meant
# to prove, since a container's own processes die with it. See NFR-003.feature
# for why this scenario is tagged @host-verified and excluded from the
# in-container behave run (app/behave.ini), and ELN.md ENTRY 016 for the
# alternatives considered (a docker-socket-proxy sidecar; installing behave on
# the host) and why this plain script won instead.
#
# Probes go through the existing "postgres" service (already on the same
# django_internal network, already shipping BusyBox wget -- postgres:17-alpine
# has no curl) rather than a new container or image, and rather than the
# host's own loopback: postgres never needs Docker control-plane access, so
# this never has to give app one either. This is a deliberate second HTTP-probe
# idiom alongside app/scripts/healthcheck.sh's curl one, not an overlooked
# duplicate: healthcheck.sh runs inside "app" itself, which is exactly the
# container this script needs to observe from outside while it's stopped.
set -eu -o pipefail

COMPOSE_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/compose.yaml"
COMPOSE=(docker compose -f "$COMPOSE_FILE")

# method, path, human label for each surface Scenario 2 names explicitly.
ENDPOINTS=(
  "GET /api/cities REST"
  "POST /api/graphql GraphQL"
  "GET /api/cities/00000000-0000-0000-0000-000000000000/forecast/feed.atom Atom"
  "GET /ws/alerts/00000000-0000-0000-0000-000000000000/ WebSocket"
  "POST /api/webhooks/github webhook"
  "GET /admin/ CMS"
)

# A stopped app container's hostname stops resolving on the docker-internal
# network entirely (Docker's embedded DNS drops it), so "bad address" is the
# actual failure text, not "connection refused" -- confirmed by running this
# probe against a deliberately stopped container before writing this check.
# Any HTTP response, even a 4xx/5xx one, proves the port is being served, so
# "server returned error: HTTP" (BusyBox wget's own wording) counts as reachable.
probe_reachable() {
  local method="$1" path="$2" output
  local extra_args=()
  if [ "$method" = "POST" ]; then
    extra_args=(--post-data "{}")
  fi
  if output=$("${COMPOSE[@]}" exec -T postgres wget -q -O /dev/null -T 3 \
      --header "Host: localhost" "${extra_args[@]}" \
      "http://app:8000${path}" 2>&1); then
    return 0
  fi
  case "$output" in
    *"server returned error: HTTP"*) return 0 ;;
    *) return 1 ;;
  esac
}

# One `docker compose exec` per endpoint (18 total across the three calls
# below) rather than batching all 6 of one phase into a single exec running a
# heredoc script: the exec overhead is a few seconds against a script whose
# `docker compose stop`/`up --wait` calls already dominate the runtime, and
# per-endpoint execs keep a failing probe's FAIL line pointing at exactly
# which endpoint/phase broke instead of requiring the batch script to be
# unpacked to find out.
assert_all() {
  local expect="$1" method path label actual
  for entry in "${ENDPOINTS[@]}"; do
    read -r method path label <<<"$entry"
    if probe_reachable "$method" "$path"; then
      actual=reachable
    else
      actual=unreachable
    fi
    if [ "$actual" != "$expect" ]; then
      echo "FAIL: $label ($method $path) was $actual, expected $expect" >&2
      exit 1
    fi
    echo "ok: $label ($method $path) is $actual"
  done
}

restore_app() {
  "${COMPOSE[@]}" up --detach --wait app >/dev/null
}
# Always leave the stack running, even if an assertion above fails midway.
trap restore_app EXIT

echo "== confirming all endpoints are reachable while app is running =="
assert_all reachable

echo "== docker compose stop app =="
"${COMPOSE[@]}" stop app >/dev/null

echo "== confirming all endpoints became unreachable together =="
assert_all unreachable

echo "== docker compose up --detach --wait app (restoring) =="
restore_app
trap - EXIT

echo "== confirming all endpoints are reachable again =="
assert_all reachable

echo "single_unit_lifecycle: app container's REST, GraphQL, Atom, WebSocket, webhook, and CMS routes started and stopped together as one unit"
