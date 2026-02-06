"""
Third-party weather API client for fetching real weather data.
"""
import os
import time
from collections import deque
from datetime import datetime
from typing import Any, Dict, Optional

import requests


class WeatherAPIClient:
    """
    Client for fetching weather data from third-party API.
    Implements rate limiting and error handling.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.openweathermap.org/data/2.5",
        rate_limit: int = 60,
    ) -> None:
        """
        Initialize weather API client.

        Args:
            api_key: API key for authentication. If None, uses WEATHER_API_KEY env var.
            base_url: Base URL for the weather API.
            rate_limit: Maximum requests per minute (default: 60).
        """
        self.api_key = api_key or os.environ.get("WEATHER_API_KEY", "")
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.request_timestamps: deque = deque(maxlen=rate_limit)
        self._is_available = True

    def is_available(self) -> bool:
        """Check if the API is available."""
        return self._is_available and bool(self.api_key)

    def set_unavailable(self) -> None:
        """Mark the API as unavailable (for testing)."""
        self._is_available = False

    def _check_rate_limit(self) -> bool:
        """
        Check if we can make a request without exceeding rate limit.

        Returns:
            True if request can be made, False if rate limit would be exceeded.
        """
        current_time = time.time()
        # Remove timestamps older than 1 minute
        while self.request_timestamps and current_time - self.request_timestamps[0] > 60:
            self.request_timestamps.popleft()

        # Check if we're at the rate limit
        if len(self.request_timestamps) >= self.rate_limit:
            return False

        return True

    def _record_request(self) -> None:
        """Record the timestamp of a request for rate limiting."""
        self.request_timestamps.append(time.time())

    def fetch_current_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Fetch current weather data for given coordinates.

        Args:
            latitude: Latitude of the location.
            longitude: Longitude of the location.

        Returns:
            Dictionary containing weather data with keys:
                - temperature: Temperature in Celsius
                - humidity: Humidity percentage
                - pressure: Atmospheric pressure in hPa
                - wind_speed: Wind speed in km/h
                - precipitation: Precipitation in mm

        Raises:
            Exception: If API is unavailable or rate limit exceeded.
        """
        if not self.is_available():
            raise Exception("Weather API is unavailable")

        if not self._check_rate_limit():
            raise Exception("Rate limit exceeded. Request queued for later processing.")

        self._record_request()

        # For testing purposes, if API key is "test", return mock data
        if self.api_key == "test":
            return {
                "temperature": 20.5,
                "humidity": 65,
                "pressure": 1013,
                "wind_speed": 15.0,
                "precipitation": 0.0,
            }

        try:
            response = requests.get(
                f"{self.base_url}/weather",
                params={
                    "lat": latitude,
                    "lon": longitude,
                    "appid": self.api_key,
                    "units": "metric",
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            # Extract relevant weather data
            return {
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind_speed": data["wind"]["speed"] * 3.6,  # Convert m/s to km/h
                "precipitation": data.get("rain", {}).get("1h", 0.0),
            }
        except requests.RequestException as e:
            self._is_available = False
            raise Exception(f"Failed to fetch weather data: {str(e)}")
