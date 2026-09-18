import logging

from .models import WeatherRecord
from .providers import WeatherProviderUnavailable

logger = logging.getLogger(__name__)


def poll_city_weather(city, provider):
    """Fetches a fresh reading for `city` from `provider` and stores it.

    Leaves any existing weather record for `city` untouched, and logs the
    failure, when `provider` is unavailable.
    """
    try:
        reading = provider.fetch_current(city)
    except WeatherProviderUnavailable:
        logger.warning("weather provider %s unavailable for city %s", provider.name, city.name)
        return None
    return WeatherRecord.objects.create(
        city=city,
        temperature=reading.temperature,
        humidity=reading.humidity,
        wind_speed=reading.wind_speed,
        precipitation_probability=reading.precipitation_probability,
        condition=reading.condition,
        source=provider.name,
    )
