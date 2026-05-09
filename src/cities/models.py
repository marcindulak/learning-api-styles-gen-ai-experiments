"""Database models for the cities app.

A :class:`City` row models one of the supported cities. The set of
supported cities is fixed by FR-009 (Tokyo, Delhi, Shanghai, Sao Paulo,
Mexico City) and seeded by the data migration ``0002_seed_cities``;
the API rejects attempts to register a sixth city.
"""

from __future__ import annotations

import uuid

from django.db import models


# The hard cap that FR-009 specifies. Defined as a module-level constant so
# the viewset and the data migration agree on the same number rather than
# duplicating the literal in two places.
SUPPORTED_CITY_LIMIT = 5


class City(models.Model):
    """A city for which the service holds weather data.

    The fields mirror the JSON payload shown in REQUIREMENTS.md
    (``name``, ``country``, ``region``, ``timezone``, ``latitude``,
    ``longitude``) so the example curl commands in that document map
    directly onto the model.
    """

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    timezone = models.CharField(max_length=64)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "cities"

    def __str__(self) -> str:
        return self.name


class WeatherRecord(models.Model):
    """A historical weather observation for one :class:`City` on one date.

    FR-006 exposes these rows through ``/api/cities/<name>/weather/history``.
    Each row is keyed by ``(city, observed_on)`` so a city has at most one
    record per day; the API treats ``observed_on`` as a date, not a
    timestamp, because the FR-006 Gherkin queries by ``?date=YYYY-MM-DD``.
    """

    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="weather_records",
    )
    observed_on = models.DateField()
    temperature = models.FloatField()
    humidity = models.FloatField(null=True, blank=True)
    wind_speed = models.FloatField(null=True, blank=True)
    pressure = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ("-observed_on",)
        unique_together = (("city", "observed_on"),)

    def __str__(self) -> str:
        return f"{self.city.name} on {self.observed_on.isoformat()}"
