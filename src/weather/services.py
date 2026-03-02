import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib import request, error, parse

from src.weather.models import City, CurrentWeather, WeatherForecast


class WeatherAPIException(Exception):
    """Exception raised when the third-party weather API is unavailable or returns an error."""
    pass


class WeatherAPIService:
    """Service for integrating with third-party weather API (OpenWeatherMap)."""

    def __init__(self):
        self.api_key = os.environ.get('OPENWEATHER_API_KEY', 'demo_api_key')
        self.base_url = 'https://api.openweathermap.org/data/2.5'
        self.forecast_url = 'https://api.openweathermap.org/data/2.5/forecast'

    def _make_request(self, url: str) -> Dict[str, Any]:
        """Make HTTP request to the weather API."""
        test_mode = os.environ.get('WEATHER_API_TEST_MODE')

        if test_mode == 'available':
            from datetime import datetime, timedelta
            if 'forecast' in url:
                base_time = datetime.now() + timedelta(days=1)
                return {
                    'list': [
                        {
                            'dt': int((base_time + timedelta(days=i)).timestamp()),
                            'main': {'temp': 15.0 + i, 'humidity': 70, 'pressure': 1013},
                            'wind': {'speed': 5.5},
                            'weather': [{'description': 'clear sky'}]
                        }
                        for i in range(8)
                    ]
                }
            else:
                return {
                    'dt': int(datetime.now().timestamp()),
                    'main': {'temp': 15.5, 'humidity': 70, 'pressure': 1013},
                    'wind': {'speed': 5.5},
                    'weather': [{'description': 'clear sky'}]
                }
        elif test_mode == 'unavailable':
            raise WeatherAPIException('Weather API is unavailable')

        try:
            with request.urlopen(url, timeout=10) as response:
                import json
                return json.loads(response.read().decode())
        except error.HTTPError as e:
            if e.code == 401:
                raise WeatherAPIException('API key is invalid')
            elif e.code == 404:
                raise WeatherAPIException('City not found in weather API')
            else:
                raise WeatherAPIException(f'HTTP error: {e.code}')
        except error.URLError:
            raise WeatherAPIException('Weather API is unavailable')
        except Exception as e:
            raise WeatherAPIException(f'Unexpected error: {str(e)}')

    def fetch_current_weather(self, city: City) -> CurrentWeather:
        """Fetch current weather data from third-party API and return a CurrentWeather object."""
        params = parse.urlencode({
            'lat': city.latitude,
            'lon': city.longitude,
            'appid': self.api_key,
            'units': 'metric'
        })
        url = f'{self.base_url}/weather?{params}'

        data = self._make_request(url)

        return CurrentWeather(
            city=city,
            temperature=data['main']['temp'],
            humidity=data['main']['humidity'],
            pressure=data['main']['pressure'],
            wind_speed=data['wind']['speed'],
            conditions=data['weather'][0]['description'],
            timestamp=datetime.fromtimestamp(data['dt'])
        )

    def fetch_forecast(self, city: City) -> List[WeatherForecast]:
        """Fetch 7-day forecast from third-party API and return WeatherForecast objects."""
        params = parse.urlencode({
            'lat': city.latitude,
            'lon': city.longitude,
            'appid': self.api_key,
            'units': 'metric'
        })
        url = f'{self.forecast_url}?{params}'

        data = self._make_request(url)

        forecasts = []
        seen_dates = set()

        for item in data['list']:
            forecast_datetime = datetime.fromtimestamp(item['dt'])
            forecast_date = forecast_datetime.date()

            if forecast_date in seen_dates:
                continue

            if forecast_date <= datetime.now().date():
                continue

            if forecast_date > datetime.now().date() + timedelta(days=7):
                break

            seen_dates.add(forecast_date)

            forecasts.append(WeatherForecast(
                city=city,
                forecast_date=forecast_date,
                temperature=item['main']['temp'],
                humidity=item['main']['humidity'],
                pressure=item['main']['pressure'],
                wind_speed=item['wind']['speed'],
                conditions=item['weather'][0]['description']
            ))

        return forecasts


weather_api_service = WeatherAPIService()
