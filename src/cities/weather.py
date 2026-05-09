"""Weather endpoints for the cities app.

Exposes:

* ``GET /api/cities/<name>/weather/current`` (FR-001) — returns the four
  common weather indicators (temperature, humidity, wind speed, pressure).
* ``GET /api/cities/<name>/weather/forecast`` (FR-010) — returns up to
  ``MAX_FORECAST_DAYS`` daily entries, defaulting to the maximum.

The values are deterministic placeholders for now; FR-008 will replace
the placeholder source with a real third-party provider and add the
``source`` envelope its scenarios assert.
"""

from __future__ import annotations

import datetime

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from .models import City


# Placeholder readings used until FR-008 introduces a real provider. Constants
# rather than randomised values so the FR-001 scenarios remain deterministic
# regardless of how often they are re-run.
_PLACEHOLDER_READING = {
    "temperature": 21.0,
    "humidity": 60.0,
    "wind_speed": 4.5,
    "pressure": 1013.0,
}


# FR-010 caps the forecast at 7 days. Module-level constant so the view body
# stays readable and a future change touches one line.
MAX_FORECAST_DAYS = 7


@api_view(["GET"])
@permission_classes([AllowAny])
def current_weather(request: Request, name: str) -> Response:
    """Return the current weather for the named city, or 404 if unknown.

    The ``name`` segment is matched case-sensitively against
    :attr:`City.name` so the URL ``/api/cities/Tokyo/weather/current``
    resolves only to the seeded "Tokyo" row.
    """

    if not City.objects.filter(name=name).exists():
        return Response(
            {"detail": f"city {name!r} not found."},
            status=404,
        )
    return Response(_PLACEHOLDER_READING)


def _parse_days(raw: str | None) -> tuple[int | None, str | None]:
    """Validate the ``?days=`` query parameter.

    Returns ``(days, None)`` on success, ``(None, error_message)`` on failure.
    The error message is the value the FR-010 Gherkin asserts via the
    ``detail`` field. ``raw is None`` defaults to :data:`MAX_FORECAST_DAYS`.
    """

    if raw is None:
        return MAX_FORECAST_DAYS, None
    try:
        value = int(raw)
    except ValueError:
        return None, f"days must be an integer between 1 and maximum 7 days."
    if value < 1:
        return None, f"days must be between 1 and maximum 7 days."
    if value > MAX_FORECAST_DAYS:
        return None, f"days exceeds the maximum 7 days horizon."
    return value, None


@api_view(["GET"])
@permission_classes([AllowAny])
def forecast(request: Request, name: str) -> Response:
    """Return up to seven daily forecast entries for the named city.

    Honours an optional ``?days=N`` query parameter (1..7). Values outside
    that range produce HTTP 400 with a ``detail`` message containing the
    phrase "maximum 7 days" so the FR-010 assertion can recognise the cap.
    """

    if not City.objects.filter(name=name).exists():
        return Response(
            {"detail": f"city {name!r} not found."},
            status=404,
        )

    days, error = _parse_days(request.query_params.get("days"))
    if error is not None:
        return Response({"detail": error}, status=400)

    today = datetime.date.today()
    results = [
        {
            "date": (today + datetime.timedelta(days=offset)).isoformat(),
            **_PLACEHOLDER_READING,
        }
        for offset in range(days)
    ]
    return Response({"count": len(results), "results": results})
