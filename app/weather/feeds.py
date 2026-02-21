"""
Atom feeds for weather forecasts using Django's syndication framework.
"""
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.urls import reverse
from .models import City, Forecast


class AllCityForecastFeed(Feed):
    """Atom feed for all weather forecasts across all cities."""

    feed_type = Atom1Feed
    title = "Weather Forecasts - All Cities"
    link = "/api/feeds/forecasts/"
    description = "7-day weather forecasts for all cities"

    def items(self):
        """Return all forecasts ordered by forecast date."""
        return Forecast.objects.select_related('city').order_by('forecast_date')[:50]

    def item_title(self, item):
        """Return title for each forecast item."""
        return f"{item.city.name} - {item.forecast_date}"

    def item_description(self, item):
        """Return description for each forecast item."""
        return (
            f"Weather forecast for {item.city.name}, {item.city.country} "
            f"on {item.forecast_date}: {item.description}. "
            f"High: {item.temperature_high}°C, Low: {item.temperature_low}°C, "
            f"Humidity: {item.humidity}%, Wind: {item.wind_speed} km/h, "
            f"Precipitation probability: {item.precipitation_probability}%"
        )

    def item_link(self, item):
        """Return link for each forecast item."""
        return f"/api/forecasts/{item.uuid}/"

    def item_pubdate(self, item):
        """Return publication date for each forecast item."""
        return item.created_at

    def item_updateddate(self, item):
        """Return last update date for each forecast item."""
        return item.created_at


class CityForecastFeed(Feed):
    """Atom feed for weather forecasts for a specific city."""

    feed_type = Atom1Feed

    def get_object(self, request, city_uuid):
        """Get the city object from the URL parameter."""
        return City.objects.get(uuid=city_uuid)

    def title(self, obj):
        """Return feed title based on city."""
        return f"Weather Forecasts - {obj.name}, {obj.country}"

    def link(self, obj):
        """Return feed link based on city."""
        return f"/api/feeds/forecasts/{obj.uuid}/"

    def description(self, obj):
        """Return feed description based on city."""
        return f"7-day weather forecasts for {obj.name}, {obj.country}"

    def items(self, obj):
        """Return forecasts for the specific city."""
        return Forecast.objects.filter(city=obj).order_by('forecast_date')

    def item_title(self, item):
        """Return title for each forecast item."""
        return f"{item.forecast_date} - {item.description}"

    def item_description(self, item):
        """Return description for each forecast item."""
        return (
            f"Weather forecast for {item.forecast_date}: {item.description}. "
            f"High: {item.temperature_high}°C, Low: {item.temperature_low}°C, "
            f"Humidity: {item.humidity}%, Wind: {item.wind_speed} km/h, "
            f"Precipitation probability: {item.precipitation_probability}%"
        )

    def item_link(self, item):
        """Return link for each forecast item."""
        return f"/api/forecasts/{item.uuid}/"

    def item_pubdate(self, item):
        """Return publication date for each forecast item."""
        return item.created_at

    def item_updateddate(self, item):
        """Return last update date for each forecast item."""
        return item.created_at
