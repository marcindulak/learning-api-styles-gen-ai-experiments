import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# World Meteorological Organization weather interpretation codes, as
# documented by Open-Meteo: https://open-meteo.com/en/docs
_CONDITION_BY_WEATHER_CODE = {
    0: "Clear",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Fog",
    51: "Drizzle",
    53: "Drizzle",
    55: "Drizzle",
    56: "Freezing Drizzle",
    57: "Freezing Drizzle",
    61: "Rain",
    63: "Rain",
    65: "Rain",
    66: "Freezing Rain",
    67: "Freezing Rain",
    71: "Snow",
    73: "Snow",
    75: "Snow",
    77: "Snow Grains",
    80: "Rain Showers",
    81: "Rain Showers",
    82: "Rain Showers",
    85: "Snow Showers",
    86: "Snow Showers",
    95: "Thunderstorm",
    96: "Thunderstorm",
    99: "Thunderstorm",
}


class WeatherProviderUnavailable(Exception):
    """Raised when the external weather data provider cannot be reached or returns an error."""


@dataclass(frozen=True)
class WeatherReading:
    temperature: float
    humidity: int
    wind_speed: float
    precipitation_probability: int
    condition: str


class OpenMeteoWeatherProvider:
    """Fetches current weather readings for a city from the Open-Meteo API.

    Open-Meteo requires no API key or registration, which keeps this
    project runnable by any reader (NFR-006) without a secret to provision.
    """

    name = "open-meteo"

    def fetch_current(self, city) -> WeatherReading:
        # precipitation_probability is only exposed in the hourly block, not
        # the current one, per the provider's actual response shape (verified
        # directly against the live API before writing this).
        query = urllib.parse.urlencode({
            "latitude": city.latitude,
            "longitude": city.longitude,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
            "hourly": "precipitation_probability",
            "forecast_days": 1,
            "timezone": "UTC",
        })
        try:
            with urllib.request.urlopen(f"{OPEN_METEO_URL}?{query}", timeout=10) as response:
                payload = json.loads(response.read())
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            raise WeatherProviderUnavailable(str(exc)) from exc

        current = payload["current"]
        current_hour = current["time"][:13] + ":00"
        # A list scan over ~24 hourly entries, not index arithmetic: this
        # stays correct even if the provider ever returns a non-contiguous
        # or differently-ordered hourly array.
        hourly_index = payload["hourly"]["time"].index(current_hour)
        precipitation_probability = payload["hourly"]["precipitation_probability"][hourly_index]

        return WeatherReading(
            temperature=current["temperature_2m"],
            humidity=round(current["relative_humidity_2m"]),
            wind_speed=current["wind_speed_10m"],
            precipitation_probability=precipitation_probability,
            condition=_CONDITION_BY_WEATHER_CODE.get(current["weather_code"], "Unknown"),
        )
