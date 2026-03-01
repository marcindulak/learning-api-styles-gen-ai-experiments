"""Atom feed for weather forecasts."""
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed

from .models import WeatherForecast


class WeatherForecastFeed(Feed):
    """Atom feed for weather forecasts."""

    feed_type = Atom1Feed
    title = 'Weather Forecast Feed'
    link = '/api/feeds/forecasts'
    subtitle = 'Latest weather forecasts for major cities'

    def items(self):
        """Return latest forecasts."""
        return WeatherForecast.objects.select_related('city').order_by('-created_at')[:50]

    def item_title(self, item: WeatherForecast) -> str:
        """Return item title."""
        return f"{item.city.name} - {item.forecast_date}"

    def item_description(self, item: WeatherForecast) -> str:
        """Return item description."""
        return (
            f"{item.weather_description}. "
            f"Temperature: {item.temperature_min}°C to {item.temperature_max}°C. "
            f"Humidity: {item.humidity}%. "
            f"Wind: {item.wind_speed} m/s. "
            f"Precipitation probability: {item.precipitation_probability}%."
        )

    def item_link(self, item: WeatherForecast) -> str:
        """Return item link."""
        return f"/api/weather-forecasts/{item.uuid}"

    def item_pubdate(self, item: WeatherForecast):
        """Return item publication date."""
        return item.created_at

    def item_updateddate(self, item: WeatherForecast):
        """Return item updated date."""
        return item.updated_at
