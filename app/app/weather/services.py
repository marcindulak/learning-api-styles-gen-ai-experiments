"""Open-Meteo API integration (https://open-meteo.com/ — free, no API key required)."""
import logging
from datetime import date, timedelta, datetime

import httpx
from django.utils.timezone import make_aware

from .models import City, WeatherForecast, WeatherRecord

logger = logging.getLogger(__name__)

OPEN_METEO_BASE = "https://api.open-meteo.com/v1"

# WMO weather code descriptions (https://open-meteo.com/en/docs#weathervariables)
_WMO_DESCRIPTIONS = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
}


def _wmo_code_to_description(code) -> str:
    if code is None:
        return ""
    return _WMO_DESCRIPTIONS.get(int(code), f"Code {code}")


def fetch_and_store_forecast(city: City) -> int:
    """Fetch 7-day forecast from Open-Meteo and upsert into WeatherForecast.

    Returns the number of forecast days imported.
    """
    url = f"{OPEN_METEO_BASE}/forecast"
    params = {
        "latitude": city.latitude,
        "longitude": city.longitude,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max,weathercode",
        "forecast_days": 7,
        "timezone": city.timezone,
    }
    with httpx.Client(timeout=10) as client:
        response = client.get(url, params=params)
        response.raise_for_status()

    daily = response.json()["daily"]
    count = 0
    for i, forecast_date_str in enumerate(daily["time"]):
        forecast_date = date.fromisoformat(forecast_date_str)
        WeatherForecast.objects.update_or_create(
            city=city,
            forecast_date=forecast_date,
            defaults={
                "temperature_max_celsius": daily["temperature_2m_max"][i] or 0.0,
                "temperature_min_celsius": daily["temperature_2m_min"][i] or 0.0,
                "precipitation_mm": daily["precipitation_sum"][i] or 0.0,
                "wind_speed_kmh": daily["windspeed_10m_max"][i] or 0.0,
                "description": _wmo_code_to_description(daily["weathercode"][i]),
            },
        )
        count += 1
    logger.info("Imported %d forecast days for city %s", count, city.name)
    return count


def fetch_and_store_historical(city: City, days_back: int = 7) -> int:
    """Fetch recent historical weather from Open-Meteo archive and store as WeatherRecords.

    Returns the number of hourly records imported (skips existing).
    """
    end_date = date.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=days_back - 1)
    url = f"{OPEN_METEO_BASE}/archive"
    params = {
        "latitude": city.latitude,
        "longitude": city.longitude,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "hourly": "temperature_2m,relativehumidity_2m,windspeed_10m,precipitation",
        "timezone": city.timezone,
    }
    with httpx.Client(timeout=30) as client:
        response = client.get(url, params=params)
        response.raise_for_status()

    hourly = response.json()["hourly"]
    count = 0
    for i, ts in enumerate(hourly["time"]):
        recorded_at = make_aware(datetime.fromisoformat(ts))
        _, created = WeatherRecord.objects.get_or_create(
            city=city,
            recorded_at=recorded_at,
            defaults={
                "temperature_celsius": hourly["temperature_2m"][i] or 0.0,
                "humidity_percent": hourly["relativehumidity_2m"][i] or 0.0,
                "wind_speed_kmh": hourly["windspeed_10m"][i] or 0.0,
                "precipitation_mm": hourly["precipitation"][i] or 0.0,
            },
        )
        if created:
            count += 1
    logger.info("Imported %d historical records for city %s", count, city.name)
    return count
