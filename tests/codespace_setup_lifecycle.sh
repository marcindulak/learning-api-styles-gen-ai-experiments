#!/usr/bin/env bash
# NFR-006 Scenario 2: "Service runs inside a GitHub Codespace without manual
# setup".
#
# Must run on the host/CI runner, never via `docker compose exec app python
# manage.py behave`, for the same reason as tests/clean_checkout_lifecycle.sh:
# the "app" container has no docker CLI/socket access to orchestrate a second
# stack. A real GitHub Codespace isn't available in this environment either
# (no GitHub Codespaces API access, and no Node.js on the host to run the
# reference "@devcontainers/cli" implementation), so this verifies the actual
# mechanism a Codespace delegates to for a docker-compose-based devcontainer
# (per the "dev container spec": read dockerComposeFile/service from
# .devcontainer/devcontainer.json, then run plain `docker compose up`) --
# not a synthetic stand-in for it. See NFR-006.feature for why this scenario
# is tagged @host-verified and excluded from the in-container behave run
# (app/behave.ini), and ELN.md ENTRY 017 for the alternatives considered
# (installing Node.js solely to run the devcontainers CLI; leaving the
# scenario unautomated/manually-verified-only).
#
# This script cannot confirm the "forwarded" half of "the service becomes
# available on the forwarded port" (VS Code/Codespaces' own port-forwarding
# UI is not reachable here either) -- it only confirms the internal listener
# devcontainer.json's forwardPorts entry names is genuinely being served, the
# same residual gap tests/clean_checkout_lifecycle.sh documents. See ELN.md
# ENTRY 017 for why compose.yaml's pinned container_name/hostname/network
# name and fixed host ports were left as-is rather than changed to avoid this
# gap: that would widen this iteration's change beyond NFR-006's own scripts,
# into shared infrastructure every other already-@status-done feature was
# built and reviewed against.
set -eu -o pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$REPO_ROOT/tests/lib/nfr_006_stack_helpers.sh"

ISOLATION_OVERRIDE="$REPO_ROOT/tests/fixtures/nfr_006_isolated_stack_override.yaml"
DEVCONTAINER_JSON="$REPO_ROOT/.devcontainer/devcontainer.json"

# One parse, one process: reads devcontainer.json once and resolves
# dockerComposeFile to an absolute path itself, rather than three separate
# `python3 -c` calls plus a bash `cd`/`pwd` round-trip for path resolution.
read -r compose_file service forward_port <<<"$(python3 - "$DEVCONTAINER_JSON" <<'PYEOF'
import json
import os
import sys

devcontainer_path = sys.argv[1]
with open(devcontainer_path) as f:
    config = json.load(f)

compose_file = os.path.normpath(
    os.path.join(os.path.dirname(devcontainer_path), config["dockerComposeFile"])
)
print(compose_file, config["service"], config["forwardPorts"][0])
PYEOF
)"

if ! docker compose -f "$compose_file" config --services | grep -qx "$service"; then
    echo "devcontainer.json's \"service\": \"$service\" is not a service defined in $compose_file" >&2
    exit 1
fi

MAIN_COMPOSE=(docker compose -f "$REPO_ROOT/compose.yaml")
PROJECT_NAME="nfr006-codespace-setup"
CODESPACE_COMPOSE=(docker compose -p "$PROJECT_NAME" -f "$compose_file" -f "$ISOLATION_OVERRIDE")

cleanup() {
    "${CODESPACE_COMPOSE[@]}" down --volumes >/dev/null 2>&1 || true
    stack_guard_restore MAIN_COMPOSE
}
trap cleanup EXIT

stack_guard_pause MAIN_COMPOSE

# The exact command NFR-006.feature asserts a Codespace's automated setup
# runs -- no build args, no extra env vars: opening a Codespace on this
# repository must succeed with zero manual input.
"${CODESPACE_COMPOSE[@]}" up --detach --wait

stack_probe_reachable CODESPACE_COMPOSE "$service" "$forward_port"

echo "codespace-setup: \"$service\" answered on its internal port $forward_port, the same port devcontainer.json declares in forwardPorts"
