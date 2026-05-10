"""Weather endpoints for the cities app.

Exposes:

* ``GET /api/cities/<name>/weather/current`` (FR-001, FR-008) — returns
  the four common weather indicators (temperature, humidity, wind speed,
  pressure). When ``settings.WEATHER_PROVIDER_URL`` is configured the
  reading is fetched from that third-party provider (FR-008) and the
  response carries ``observed_at`` plus ``source.provider``; otherwise
  the deterministic placeholder defined here is returned (FR-001).
* ``GET /api/cities/<name>/weather/forecast`` (FR-010) — returns up to
  ``MAX_FORECAST_DAYS`` daily entries, defaulting to the maximum.
* ``GET /api/cities/<name>/weather/history`` (FR-006) — returns stored
  observations for the named city, optionally filtered by ``?date=``.
"""

from __future__ import annotations

import datetime

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from . import providers
from .models import City, WeatherRecord


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

    When ``settings.WEATHER_PROVIDER_URL`` is configured (FR-008) the
    reading is fetched from the third-party provider and a 503 is
    returned if the provider cannot be reached. When unconfigured, the
    FR-001 deterministic placeholder is returned so the simpler scenarios
    keep passing without provider plumbing.
    """

    city = City.objects.filter(name=name).first()
    if city is None:
        return Response(
            {"detail": f"city {name!r} not found."},
            status=404,
        )

    if not providers.is_configured():
        return Response(_PLACEHOLDER_READING)

    try:
        reading = providers.fetch_current(
            latitude=float(city.latitude),
            longitude=float(city.longitude),
        )
    except providers.ProviderError as exc:
        return Response(
            {"detail": f"weather provider unavailable: {exc}"},
            status=503,
        )
    return Response(reading)


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


def _parse_date(raw: str | None) -> tuple[datetime.date | None, str | None]:
    """Validate the ``?date=`` query parameter.

    Returns ``(date, None)`` on success or ``(None, error_message)`` on
    failure. ``raw is None`` is success with ``date=None`` so the caller
    can distinguish "no filter" from a bad value.
    """

    if raw is None:
        return None, None
    try:
        return datetime.date.fromisoformat(raw), None
    except ValueError:
        return None, f"date must be in YYYY-MM-DD format."


@api_view(["GET"])
@permission_classes([AllowAny])
def history(request: Request, name: str) -> Response:
    """Return stored historical weather rows for the named city.

    Honours an optional ``?date=YYYY-MM-DD`` query parameter that filters
    results to a single observation date. A request for a date with no
    stored records returns HTTP 200 with ``results: []`` (the FR-006
    Gherkin asserts a 200 + empty list, not a 404).
    """

    city = City.objects.filter(name=name).first()
    if city is None:
        return Response(
            {"detail": f"city {name!r} not found."},
            status=404,
        )

    observed_on, error = _parse_date(request.query_params.get("date"))
    if error is not None:
        return Response({"detail": error}, status=400)

    records = city.weather_records.all()
    if observed_on is not None:
        records = records.filter(observed_on=observed_on)

    results = [
        {
            "observed_on": record.observed_on.isoformat(),
            "temperature": record.temperature,
            "humidity": record.humidity,
            "wind_speed": record.wind_speed,
            "pressure": record.pressure,
        }
        for record in records
    ]
    return Response({"count": len(results), "results": results})
