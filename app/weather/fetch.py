"""Client for the third-party weather API (Open-Meteo).

The base URL is settings.WEATHER_API_BASE_URL so tests can point the
fetch tasks at a stub server. Open-Meteo needs no API key, keeping the
service runnable without credentials.
"""
from datetime import date, datetime, timezone as dt_timezone

import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

from weather.models import MAX_FORECAST_DAYS, ForecastRecord, WeatherRecord

SOURCE = "open-meteo"

CURRENT_INDICATORS = (
    "temperature_2m,relative_humidity_2m,wind_speed_10m,"
    "surface_pressure,precipitation"
)
DAILY_INDICATORS = "temperature_2m_min,temperature_2m_max"


class WeatherFetchError(Exception):
    """Raised when the third-party weather API cannot provide data."""


def _request(params):
    url = f"{settings.WEATHER_API_BASE_URL}/v1/forecast"
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as error:
        raise WeatherFetchError(
            f"third-party weather API request failed: {error}"
        ) from error


def _observed_at(value):
    # Open-Meteo returns naive ISO timestamps when timezone=UTC is requested.
    if not value:
        return timezone.now()
    observed = datetime.fromisoformat(value)
    if observed.tzinfo is None:
        observed = observed.replace(tzinfo=dt_timezone.utc)
    return observed


def fetch_weather(city):
    """Fetch the current weather for a city and store a WeatherRecord."""
    data = _request(
        {
            "latitude": city.latitude,
            "longitude": city.longitude,
            "current": CURRENT_INDICATORS,
            "wind_speed_unit": "ms",
            "timezone": "UTC",
        }
    )
    try:
        current = data["current"]
        return WeatherRecord.objects.create(
            city=city,
            observed_at=_observed_at(current.get("time")),
            temperature=current["temperature_2m"],
            humidity=current["relative_humidity_2m"],
            wind_speed=current["wind_speed_10m"],
            pressure=current["surface_pressure"],
            precipitation=current["precipitation"],
            source=SOURCE,
        )
    except (KeyError, TypeError, ValidationError) as error:
        raise WeatherFetchError(
            f"unexpected third-party weather API response: {error}"
        ) from error


def fetch_forecast(city):
    """Fetch the daily forecast for a city and store ForecastRecords.

    Re-fetching updates existing records in place, respecting the
    one-forecast-per-city-per-day constraint.
    """
    data = _request(
        {
            "latitude": city.latitude,
            "longitude": city.longitude,
            "daily": DAILY_INDICATORS,
            "forecast_days": MAX_FORECAST_DAYS,
            "timezone": "UTC",
        }
    )
    try:
        daily = data["daily"]
        rows = zip(
            daily["time"],
            daily["temperature_2m_min"],
            daily["temperature_2m_max"],
            strict=True,
        )
        records = []
        for day, temperature_min, temperature_max in rows:
            record, _ = ForecastRecord.objects.update_or_create(
                city=city,
                forecast_date=date.fromisoformat(day),
                defaults={
                    "temperature_min": temperature_min,
                    "temperature_max": temperature_max,
                    "source": SOURCE,
                },
            )
            records.append(record)
        return records
    except (KeyError, TypeError, ValueError, ValidationError) as error:
        raise WeatherFetchError(
            f"unexpected third-party weather API response: {error}"
        ) from error
