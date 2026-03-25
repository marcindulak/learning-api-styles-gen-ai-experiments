from django.contrib.syndication.views import Feed
from .models import WeatherForecast


class WeatherForecastFeed(Feed):
    title = "Weather Forecast Service - 7-Day Forecasts"
    link = "/feed/forecasts/"
    description = "7-day weather forecasts for the world's biggest cities."

    def items(self):
        return WeatherForecast.objects.select_related("city").order_by("-updated_at")[:50]

    def item_title(self, item):
        return f"{item.city.name}: {item.forecast_date} — {item.description or 'Forecast'}"

    def item_description(self, item):
        return (
            f"Date: {item.forecast_date}\n"
            f"High: {item.temperature_max_celsius}°C  Low: {item.temperature_min_celsius}°C\n"
            f"Wind: {item.wind_speed_kmh} km/h  Precipitation: {item.precipitation_mm} mm"
        )

    def item_pubdate(self, item):
        return item.updated_at

    def item_link(self, item):
        return f"/api/forecasts/{item.uuid}"
