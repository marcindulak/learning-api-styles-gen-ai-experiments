# Shared helpers for NFR-006's host-verified lifecycle scripts
# (tests/clean_checkout_lifecycle.sh, tests/codespace_setup_lifecycle.sh).
# Source this file; it deliberately doesn't set its own shell options so it
# never overrides the sourcing script's `set -eu -o pipefail`.

# Stops the caller's already-running main dev stack (if any) so a throwaway
# stack can bind compose.yaml's fixed host ports without a conflict. Takes
# the name of an array variable holding the `docker compose -f ...` argv
# (e.g. "MAIN_COMPOSE"). Sets MAIN_STACK_WAS_RUNNING for stack_guard_restore.
stack_guard_pause() {
    local -n compose_ref=$1
    MAIN_STACK_WAS_RUNNING=""
    if [ -n "$("${compose_ref[@]}" ps --quiet)" ]; then
        MAIN_STACK_WAS_RUNNING=1
    fi
    "${compose_ref[@]}" stop
}

# Restores the main dev stack if stack_guard_pause found it running before.
stack_guard_restore() {
    local -n compose_ref=$1
    if [ -n "$MAIN_STACK_WAS_RUNNING" ]; then
        "${compose_ref[@]}" up --detach --wait
    fi
}

# Probes a throwaway stack's service for HTTP reachability via its own
# "postgres" container over the internal Docker network -- never a host-side
# curl to localhost. This sandbox's own shell has no listener on the
# published ports at all (confirmed via `ss -ltn`, ELN.md ENTRY 017) even
# though `docker port`/`docker compose ps` report them bound to 127.0.0.1;
# the Docker daemon's published ports and this shell are not in the same
# network namespace. Reuses tests/single_unit_lifecycle.sh's (ELN.md ENTRY
# 016) established "server returned error: HTTP" convention: BusyBox wget's
# own wording for any non-2xx HTTP response, which still proves the port is
# being served.
stack_probe_reachable() {
    local -n compose_ref=$1
    local host="$2" port="$3" output
    if output=$("${compose_ref[@]}" exec -T postgres wget -q -O /dev/null -T 5 \
        --header "Host: localhost" "http://${host}:${port}/admin/login/" 2>&1); then
        return 0
    fi
    [[ "$output" == *"server returned error: HTTP"* ]]
}
