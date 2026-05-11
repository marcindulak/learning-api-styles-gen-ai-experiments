"""Atom feed for the seven-day weather forecast (FR-004).

Builds on Django's ``django.contrib.syndication`` framework and renders
the same placeholder forecast that ``cities.weather.forecast`` exposes
as JSON. The entry list mirrors the JSON forecast (7 daily entries
starting from today) so the two surfaces stay in sync until FR-008
swaps the placeholder source for a real third-party provider.

URL: ``GET /feeds/forecast/<name>`` -> ``application/atom+xml`` body.
"""

from __future__ import annotations

import dataclasses
import datetime

from django.contrib.syndication.views import Feed
from django.http import Http404
from django.utils.feedgenerator import Atom1Feed

from .models import City
from .weather import MAX_FORECAST_DAYS, _PLACEHOLDER_READING


@dataclasses.dataclass(frozen=True)
class _ForecastEntry:
    """One forecast row carrying both the city name and the target date.

    ``Feed.item_link`` only receives the entry object, not the parent
    object, so the entry has to carry enough context to produce a
    unique link without re-querying the parent City.
    """

    city_name: str
    date: datetime.date


class ForecastFeed(Feed):
    """Seven-day Atom 1.0 forecast feed for a single city."""

    feed_type = Atom1Feed

    def get_object(self, request, name: str) -> City:
        try:
            return City.objects.get(name=name)
        except City.DoesNotExist as exc:
            raise Http404(f"city {name!r} not found.") from exc

    def title(self, obj: City) -> str:
        return f"Weather forecast for {obj.name}"

    def link(self, obj: City) -> str:
        return f"/feeds/forecast/{obj.name}"

    def description(self, obj: City) -> str:
        return f"{MAX_FORECAST_DAYS}-day weather forecast for {obj.name}."

    def items(self, obj: City) -> list[_ForecastEntry]:
        today = datetime.date.today()
        return [
            _ForecastEntry(
                city_name=obj.name,
                date=today + datetime.timedelta(days=offset),
            )
            for offset in range(MAX_FORECAST_DAYS)
        ]

    def item_title(self, item: _ForecastEntry) -> str:
        return f"Forecast for {item.city_name} on {item.date.isoformat()}"

    def item_description(self, item: _ForecastEntry) -> str:
        reading = _PLACEHOLDER_READING
        return (
            f"Temperature: {reading['temperature']} C, "
            f"humidity: {reading['humidity']} %, "
            f"wind speed: {reading['wind_speed']} m/s, "
            f"pressure: {reading['pressure']} hPa."
        )

    def item_link(self, item: _ForecastEntry) -> str:
        return f"/feeds/forecast/{item.city_name}#{item.date.isoformat()}"

    def item_pubdate(self, item: _ForecastEntry) -> datetime.datetime:
        # Atom 1.0 requires an <updated> element per entry. Anchor each
        # forecast entry to UTC midnight of its target date so the
        # timestamp is deterministic and timezone-explicit.
        return datetime.datetime.combine(
            item.date,
            datetime.time.min,
            tzinfo=datetime.timezone.utc,
        )
