"""Step definitions for FR-008: Weather records contain actual data.

The two FR-008 scenarios exercise the third-party weather provider plumbing
introduced in :mod:`cities.providers`:

* "configured" path — the response carries ``source.provider``,
  ``observed_at`` and the four weather indicators populated from the
  provider's payload.
* "unreachable" path — the response is HTTP 503 because the provider
  cannot be reached.

For testing, a small stdlib HTTP server is spun up in-process. CLAUDE.md
prefers a real running test instance over a mock; ``http.server`` from
the standard library satisfies this without adding a dependency. The
server is started lazily on first use and torn down via ``atexit`` so it
survives across scenarios that need it.

Reused steps from earlier features:

* ``the service is running`` (FR-007).
* ``a city named "..." exists`` (FR-011).
* ``a client sends GET to "..."`` (FR-009).
* ``the response status is N`` (FR-007).
* ``the response body has a key "..." with a numeric value`` (FR-001).
"""

from __future__ import annotations

import atexit
import datetime
import http.server
import json
import socket
import threading

from behave import given, then


# A canned Open-Meteo-shaped payload the stub server returns to every
# request. The provider client in :mod:`cities.providers` reshapes this
# into the response the FR-008 scenarios assert on. The ``time`` field
# uses a fixed value so a future scenario that pinned a golden response
# would have a stable input to compare against.
_STUB_PAYLOAD = {
    "current": {
        "time": "2026-05-10T12:00",
        "temperature_2m": 22.5,
        "relative_humidity_2m": 65,
        "wind_speed_10m": 3.2,
        "surface_pressure": 1015.0,
    }
}


class _StubProviderHandler(http.server.BaseHTTPRequestHandler):
    """HTTP handler that returns a fixed JSON payload for any GET request.

    The provider client appends a query string to the configured URL; the
    handler ignores the path entirely and always returns ``_STUB_PAYLOAD``
    so the test does not depend on URL parsing details. Logging is
    silenced because behave captures stderr by default and the server
    logs would otherwise leak into failure reports.
    """

    def do_GET(self) -> None:  # noqa: N802 (BaseHTTPRequestHandler API)
        body = json.dumps(_STUB_PAYLOAD).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        return


_stub_server: http.server.HTTPServer | None = None
_stub_thread: threading.Thread | None = None
_stub_url: str | None = None


def _ensure_stub_server() -> str:
    """Start the stub HTTP server on first use and return its base URL.

    Subsequent calls reuse the running instance. The server binds to
    ``127.0.0.1`` on a random free port (``port=0``) so concurrent runs
    on the same host do not collide.
    """

    global _stub_server, _stub_thread, _stub_url
    if _stub_url is not None:
        return _stub_url

    server = http.server.HTTPServer(("127.0.0.1", 0), _StubProviderHandler)
    thread = threading.Thread(
        target=server.serve_forever,
        name="fr-008-stub-provider",
        daemon=True,
    )
    thread.start()

    host, port = server.server_address[:2]
    _stub_server = server
    _stub_thread = thread
    _stub_url = f"http://{host}:{port}/v1/forecast"

    # Test process is short-lived; atexit is enough — no per-scenario
    # teardown is needed because the stub holds no per-scenario state.
    atexit.register(_shutdown_stub_server)
    return _stub_url


def _shutdown_stub_server() -> None:
    global _stub_server, _stub_thread, _stub_url
    if _stub_server is not None:
        _stub_server.shutdown()
        _stub_server.server_close()
    _stub_server = None
    _stub_thread = None
    _stub_url = None


def _override_provider_url(context, url: str) -> None:
    """Override ``WEATHER_PROVIDER_URL`` for the current scenario only.

    Mirrors the FR-003 webhook-secret pattern (ENTRY 009): use
    ``override_settings`` and register the disable callable on
    ``context.scenario_cleanups`` so ``after_scenario`` reverts it.
    """

    from django.test.utils import override_settings

    override = override_settings(WEATHER_PROVIDER_URL=url)
    override.enable()
    context.scenario_cleanups.append(override.disable)


def _unreachable_url() -> str:
    """Return an URL on a 127.0.0.1 port no one is listening on.

    Bind to port 0 to let the OS pick a free port, then close the socket.
    Reusing the just-released port for an HTTP request races against the
    OS reassigning it, but on Linux the kernel keeps a freed port out of
    rotation long enough for the test's single connection attempt to
    fail with ECONNREFUSED.
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    return f"http://127.0.0.1:{port}/v1/forecast"


@given('the third-party weather provider is configured')
def step_provider_configured(context) -> None:
    url = _ensure_stub_server()
    _override_provider_url(context, url)


@given('the third-party weather provider is unreachable')
def step_provider_unreachable(context) -> None:
    _override_provider_url(context, _unreachable_url())


def _decode_json(context):
    """Parse the latest response body as JSON, caching it on the context."""

    if not hasattr(context, "response_json") or context.response_json is None:
        context.response_json = json.loads(
            context.response.content.decode("utf-8")
        )
    return context.response_json


def _resolve_path(body, key: str):
    """Walk a dotted/indexed key path like ``source.provider``.

    Duplicated from fr_001/fr_006/fr_009 because behave loads step files
    via ``exec_file`` rather than Python's import machinery, so a sibling
    import would not work at load time. CLAUDE.md prefers WET over a
    fragile cross-step-file dependency for a helper this small.
    """

    current = body
    for segment in key.split("."):
        index = None
        if "[" in segment and segment.endswith("]"):
            attr, _, rest = segment.partition("[")
            index = int(rest[:-1])
        else:
            attr = segment
        if not isinstance(current, dict) or attr not in current:
            raise KeyError(
                f"Cannot resolve {key!r}: missing {attr!r} in {current!r}."
            )
        current = current[attr]
        if index is not None:
            if not isinstance(current, list) or index >= len(current):
                raise KeyError(
                    f"Cannot resolve {key!r}: index {index} out of range "
                    f"in {current!r}."
                )
            current = current[index]
    return current


@then('the response body has a key "{key}" with a non-empty string value')
def step_response_key_nonempty_string(context, key: str) -> None:
    body = _decode_json(context)
    value = _resolve_path(body, key)
    assert isinstance(value, str) and value, (
        f"Expected non-empty string at {key!r}, got {value!r} "
        f"({type(value).__name__})."
    )


@then('the response body has a key "{key}" with a value not equal to "{forbidden}"')
def step_response_key_not_equal(context, key: str, forbidden: str) -> None:
    body = _decode_json(context)
    value = _resolve_path(body, key)
    assert value != forbidden, (
        f"Expected {key!r} to differ from {forbidden!r}, got {value!r}."
    )


@then('the response body has a key "{key}" with an ISO 8601 timestamp string')
def step_response_key_iso_timestamp(context, key: str) -> None:
    body = _decode_json(context)
    value = _resolve_path(body, key)
    assert isinstance(value, str), (
        f"Expected string ISO 8601 timestamp at {key!r}, got {value!r} "
        f"({type(value).__name__})."
    )
    # ``datetime.fromisoformat`` accepts ``Z`` suffixes since Python 3.11.
    # The Dockerfile pins Python 3.13 (see ENTRY 002), so this works in
    # the test container; the fallback below handles older Pythons that
    # may run plain ``behave`` outside the container.
    candidate = value
    try:
        datetime.datetime.fromisoformat(candidate)
    except ValueError as exc:  # pragma: no cover (3.11+ accepts ``Z``)
        if candidate.endswith("Z"):
            try:
                datetime.datetime.fromisoformat(candidate[:-1] + "+00:00")
            except ValueError:
                raise AssertionError(
                    f"Expected ISO 8601 timestamp at {key!r}, got {value!r}."
                ) from exc
        else:
            raise AssertionError(
                f"Expected ISO 8601 timestamp at {key!r}, got {value!r}."
            ) from exc
