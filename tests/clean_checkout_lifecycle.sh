#!/usr/bin/env bash
# NFR-006 Scenario 1: "Service builds and runs from a clean checkout using
# only Docker".
#
# Must run on the host/CI runner, never via `docker compose exec app python
# manage.py behave`: the "app" container has no docker CLI/socket access (see
# ELN.md ENTRY 015, which rejected Docker-outside-of-Docker for NFR-001 on the
# same security grounds), so it cannot itself build/run a second, independent
# stack from a fresh clone. See NFR-006.feature for why this scenario is
# tagged @host-verified and excluded from the in-container behave run
# (app/behave.ini), and ELN.md ENTRY 017 for the alternatives considered (a
# docker-compose port-override file; leaving the scenario unautomated).
#
# A genuinely clean checkout means only committed content, with no host-only
# state (build caches, .env files, etc.) that a reader following this
# project's own README wouldn't have -- a local `git clone` of this same
# repository achieves exactly that, without needing network access to a
# remote.
#
# Runs the freshly-cloned stack on the project's own documented ports
# (8000/8001/8443/5432), matching how a first-time reader would actually run
# it -- freed for the duration of this script by pausing the already-running
# dev stack (restored afterward), rather than remapped: confirmed via
# `docker compose config` (ELN.md ENTRY 017) that Compose concatenates rather
# than replaces a service's "ports" list across merged files, so a
# port-remapping override file would still try to bind the base ports too.
#
# compose.yaml pins each service's container_name/hostname and the network's
# name to fixed strings (not project-name-prefixed), so a second project
# using the same compose.yaml collides on those even while the main stack is
# merely stopped (a stopped container still holds its name). Confirmed
# empirically (ELN.md ENTRY 017) that `!reset null` in an override file makes
# Compose fall back to its normal project-scoped auto-naming for these
# specific scalar keys, unlike the list-concatenation behavior above --
# tests/fixtures/nfr_006_isolated_stack_override.yaml applies that reset.
# (Dropping these pins, and the fixed host ports, from compose.yaml itself
# was considered and rejected for this iteration -- see ELN.md ENTRY 017:
# compose.yaml is shared infrastructure every other already-@status-done
# feature's scenarios were built and reviewed against, so widening this
# change beyond NFR-006's own two scripts was judged out of scope.)
set -eu -o pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$REPO_ROOT/tests/lib/nfr_006_stack_helpers.sh"

ISOLATION_OVERRIDE="$REPO_ROOT/tests/fixtures/nfr_006_isolated_stack_override.yaml"
MAIN_COMPOSE=(docker compose -f "$REPO_ROOT/compose.yaml")
CHECKOUT_DIR="$(mktemp -d)"
PROJECT_NAME="nfr006-clean-checkout"
CHECKOUT_COMPOSE=(docker compose -p "$PROJECT_NAME" -f "$CHECKOUT_DIR/compose.yaml" -f "$ISOLATION_OVERRIDE")

cleanup() {
    "${CHECKOUT_COMPOSE[@]}" down --volumes >/dev/null 2>&1 || true
    rm -rf "$CHECKOUT_DIR"
    stack_guard_restore MAIN_COMPOSE
}
trap cleanup EXIT

stack_guard_pause MAIN_COMPOSE

git clone --quiet "$REPO_ROOT" "$CHECKOUT_DIR"

# The exact commands from REQUIREMENTS.md's own "Service is runnable" section.
"${CHECKOUT_COMPOSE[@]}" build --build-arg UID="$(id -u)" --build-arg GID="$(id -g)"
"${CHECKOUT_COMPOSE[@]}" up --detach --wait

stack_probe_reachable CHECKOUT_COMPOSE app 8000

echo "clean-checkout: service answered on its internal port 8000 (mapped to host 127.0.0.1:8000 by compose.yaml) from a fresh clone"
