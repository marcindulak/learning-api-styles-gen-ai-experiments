"""Seed data for the supported cities (FR-009).

This module is the single source of truth for the five supported city
records. Both the data migration and the behave ``before_scenario`` hook
import :data:`SEED_CITIES` and call :func:`seed_cities`, so the two paths
can never drift apart.

The hook is needed because behave-django's default runner uses
:class:`django.test.LiveServerTestCase`, which truncates the database
between scenarios. Without re-seeding, the rows the data migration
inserted at ``setup_databases`` time would only be visible to the first
scenario.
"""

from __future__ import annotations

from typing import Iterable


# (name, country, region, IANA timezone, latitude, longitude). The list is
# sorted alphabetically by name to match ``City.Meta.ordering``; matching
# orders make diffs and assertion failures easier to read.
SEED_CITIES: tuple[tuple[str, str, str, str, str, str], ...] = (
    ("Delhi", "India", "Asia", "Asia/Kolkata", "28.613900", "77.209000"),
    ("Mexico City", "Mexico", "Americas", "America/Mexico_City", "19.432600", "-99.133200"),
    ("Sao Paulo", "Brazil", "Americas", "America/Sao_Paulo", "-23.550500", "-46.633300"),
    ("Shanghai", "China", "Asia", "Asia/Shanghai", "31.230400", "121.473700"),
    ("Tokyo", "Japan", "Asia", "Asia/Tokyo", "35.689500", "139.691700"),
)


def seed_cities(model_class) -> None:
    """Insert or update the supported cities using ``model_class``.

    Accepts both the runtime ``cities.models.City`` and the historical
    model returned by ``apps.get_model("cities", "City")`` inside a
    migration; both expose the same ``objects.update_or_create`` API.
    """

    rows: Iterable[tuple[str, str, str, str, str, str]] = SEED_CITIES
    for name, country, region, timezone, latitude, longitude in rows:
        model_class.objects.update_or_create(
            name=name,
            defaults={
                "country": country,
                "region": region,
                "timezone": timezone,
                "latitude": latitude,
                "longitude": longitude,
            },
        )
