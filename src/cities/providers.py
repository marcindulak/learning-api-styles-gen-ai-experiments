"""Third-party weather provider client (FR-008).

Until FR-008, ``cities.weather.current_weather`` returned a deterministic
placeholder reading. FR-008 introduces a real third-party provider whose
response is reshaped into the application's reading dict and wrapped with
a ``source.provider`` envelope plus an ``observed_at`` timestamp.

The default provider is `Open-Meteo <https://open-meteo.com/>`_ — a free
weather API that requires no API key. The base URL is configurable via
``settings.WEATHER_PROVIDER_URL`` so tests can point the client at a
local stub HTTP server (see ``features/environment.py``) and the
unreachable-provider scenario can point it at a closed port.
"""

from __future__ import annotations

import datetime
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from django.conf import settings


PROVIDER_NAME = "open-meteo"

# 5-second timeout matches the WebSocket/live-HTTP timeout already used in
# nfr_001_steps and the FR-005 Gherkin so the suite's failure-mode timing
# stays consistent across features.
_HTTP_TIMEOUT_SECONDS = 5.0


class ProviderError(RuntimeError):
    """Raised when the third-party provider cannot be reached or parsed."""


def is_configured() -> bool:
    """Return True iff a provider base URL is configured."""

    return bool(getattr(settings, "WEATHER_PROVIDER_URL", ""))


def fetch_current(latitude: float, longitude: float) -> dict[str, Any]:
    """Fetch the current weather for the given coordinates.

    Builds an Open-Meteo-compatible query (``current=<comma-list>``) and
    converts the response into the dict shape the ``current_weather``
    view returns to clients. The mapping is:

    * ``current.temperature_2m`` -> ``temperature``
    * ``current.relative_humidity_2m`` -> ``humidity``
    * ``current.wind_speed_10m`` -> ``wind_speed``
    * ``current.surface_pressure`` -> ``pressure``
    * ``current.time`` -> ``observed_at`` (normalised to a ``Z``-suffixed
      ISO 8601 string when no timezone is present)

    Raises :class:`ProviderError` for any network, decoding, or shape
    failure so the caller can return HTTP 503 in one place.
    """

    base_url = settings.WEATHER_PROVIDER_URL
    query = urllib.parse.urlencode(
        {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,surface_pressure",
        }
    )
    separator = "&" if "?" in base_url else "?"
    url = f"{base_url}{separator}{query}"

    try:
        with urllib.request.urlopen(url, timeout=_HTTP_TIMEOUT_SECONDS) as response:
            raw = response.read()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ProviderError(f"provider request failed: {exc}") from exc

    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProviderError(f"provider response was not valid JSON: {exc}") from exc

    current = payload.get("current") if isinstance(payload, dict) else None
    if not isinstance(current, dict):
        raise ProviderError("provider response missing 'current' object.")

    try:
        return {
            "temperature": float(current["temperature_2m"]),
            "humidity": float(current["relative_humidity_2m"]),
            "wind_speed": float(current["wind_speed_10m"]),
            "pressure": float(current["surface_pressure"]),
            "observed_at": _normalise_timestamp(current["time"]),
            "source": {"provider": PROVIDER_NAME},
        }
    except (KeyError, TypeError, ValueError) as exc:
        raise ProviderError(f"provider response missing expected fields: {exc}") from exc


def _normalise_timestamp(raw: str) -> str:
    """Return an ISO 8601 string with an explicit UTC offset.

    Open-Meteo returns ``"2026-05-10T12:00"`` (naive, UTC by API contract).
    Adding ``Z`` makes the timezone explicit so downstream consumers do
    not have to know the API convention to interpret the value.
    """

    parsed = datetime.datetime.fromisoformat(raw)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.timezone.utc)
    # ``isoformat`` emits ``+00:00`` for UTC; rewrite it to ``Z`` so the
    # value matches the shape most JSON consumers expect.
    return parsed.isoformat().replace("+00:00", "Z")
