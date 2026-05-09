"""Current-weather endpoint for FR-001.

Exposes ``GET /api/cities/<name>/weather/current`` and returns the four
common weather indicators (temperature, humidity, wind speed, pressure).
The values are deterministic placeholders for now; FR-008 will replace
the placeholder source with a real third-party provider and add the
``source`` envelope its scenarios assert.
"""

from __future__ import annotations

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
