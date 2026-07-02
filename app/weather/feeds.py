"""Atom feed publishing the weather forecast of a city."""
from datetime import datetime, time, timedelta, timezone

from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.utils import timezone as django_timezone
from django.utils.feedgenerator import Atom1Feed

from weather.models import MAX_FORECAST_DAYS, City


class CityForecastFeed(Feed):
    """Serves the upcoming forecast records of a city as Atom entries.

    The item window mirrors CityForecastView: today up to
    MAX_FORECAST_DAYS ahead, ordered by forecast date.
    """

    feed_type = Atom1Feed

    def get_object(self, request, uuid):
        return get_object_or_404(City, uuid=uuid)

    def title(self, obj):
        return f"Weather forecast for {obj.name}"

    def subtitle(self, obj):
        return f"Daily weather forecast for {obj.name}, {obj.country}"

    def link(self, obj):
        return f"/api/cities/{obj.uuid}/forecast/feed"

    def items(self, obj):
        today = django_timezone.localdate()
        return obj.forecast_records.filter(
            forecast_date__gte=today,
            forecast_date__lte=today + timedelta(days=MAX_FORECAST_DAYS),
        ).order_by("forecast_date")

    def item_title(self, item):
        return f"{item.city.name} forecast for {item.forecast_date:%Y-%m-%d}"

    def item_description(self, item):
        return (
            f"Minimum temperature {item.temperature_min} °C, "
            f"maximum temperature {item.temperature_max} °C."
        )

    def item_link(self, item):
        return f"/api/cities/{item.city.uuid}/forecast?date={item.forecast_date}"

    def item_updateddate(self, item):
        return datetime.combine(item.forecast_date, time.min, tzinfo=timezone.utc)
