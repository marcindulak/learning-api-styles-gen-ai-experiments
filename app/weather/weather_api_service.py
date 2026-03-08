"""
Service for integrating with third-party weather APIs.
"""
import os
from datetime import date, timedelta
from typing import Optional


class WeatherAPIService:
    """
    Service for fetching weather data from third-party APIs.
    In test mode, returns mock data. In production, would call real API.
    """

    def _get_test_mode(self):
        """Get current test mode from environment variable."""
        return os.environ.get('WEATHER_API_TEST_MODE', 'available')

    def fetch_current_weather(self, city_name: str, latitude: float, longitude: float) -> Optional[dict]:
        """
        Fetch current weather data for a city.

        Args:
            city_name: Name of the city
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Dictionary with weather data or None if API is unavailable
        """
        if self._get_test_mode() == 'unavailable':
            return None

        return {
            'temperature': 20.5,
            'humidity': 65.0,
            'pressure': 1013.25,
            'wind_speed': 5.5
        }

    def fetch_forecast(self, city_name: str, latitude: float, longitude: float, days: int = 7) -> Optional[list]:
        """
        Fetch weather forecast data for a city.

        Args:
            city_name: Name of the city
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            days: Number of days to forecast (default 7)

        Returns:
            List of forecast dictionaries or None if API is unavailable
        """
        if self._get_test_mode() == 'unavailable':
            return None

        forecasts = []
        today = date.today()

        for i in range(1, days + 1):
            forecast_date = today + timedelta(days=i)
            forecasts.append({
                'forecast_date': forecast_date.isoformat(),
                'temperature': 18.0 + i * 0.5,
                'humidity': 60.0 + i * 2,
                'pressure': 1010.0 + i,
                'wind_speed': 4.0 + i * 0.3
            })

        return forecasts
