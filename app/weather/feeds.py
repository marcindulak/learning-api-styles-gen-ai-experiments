"""Atom feed for weather forecasts."""

from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed

from .models import WeatherForecast


class ForecastAtomFeed(Feed):
    feed_type = Atom1Feed
    title = "Weather Forecast Service \u2014 Forecasts"
    link = "/api/feed/forecasts"
    subtitle = "Latest weather forecasts for major cities."

    def get_object(self, request):
        return request.GET.get("city")

    def items(self, obj):
        qs = WeatherForecast.objects.select_related("city").order_by("-updated_at")
        if obj:
            qs = qs.filter(city__uuid=obj)
        return qs[:50]

    def item_title(self, item):
        return f"{item.city.name} — {item.forecast_date}"

    def item_description(self, item):
        return (
            f"{item.description}. "
            f"High: {item.temperature_high}°C, Low: {item.temperature_low}°C."
        )

    def item_updateddate(self, item):
        return item.updated_at

    def item_link(self, item):
        return f"/api/cities/{item.city.uuid}/forecast"

    def item_guid(self, item):
        return str(item.uuid)
