"""Weather service for fetching weather data.

This module provides weather data for cities. In a production environment,
this would integrate with a real 3rd party API like OpenWeatherMap.
For this educational implementation, it generates realistic weather data
based on geographical location and season.
"""
import random
from datetime import date, datetime, timedelta
from typing import Any

from django.utils import timezone

from .models import City


def _get_base_temperature(latitude: float, month: int) -> float:
    """Calculate base temperature based on latitude and month."""
    # Simplified seasonal temperature calculation
    # Northern hemisphere: summer = months 6-8, winter = months 12-2
    # Southern hemisphere: reversed

    hemisphere_factor = 1 if latitude >= 0 else -1
    season_offset = abs(month - 6) * hemisphere_factor

    # Base temperature decreases with distance from equator
    equator_distance = abs(latitude)
    base_temp = 30 - (equator_distance * 0.5)

    # Seasonal variation
    seasonal_variation = season_offset * 3

    return base_temp + seasonal_variation


def generate_current_weather(city: City) -> dict[str, Any]:
    """Generate realistic current weather data for a city."""
    now = timezone.now()
    month = now.month

    base_temp = _get_base_temperature(city.latitude, month)
    temperature = base_temp + random.uniform(-5, 5)
    feels_like = temperature + random.uniform(-3, 3)

    conditions = ['Clear', 'Clouds', 'Rain', 'Drizzle', 'Thunderstorm', 'Snow', 'Mist']
    weights = [30, 25, 15, 10, 5, 5, 10]  # Clear weather more likely
    condition = random.choices(conditions, weights=weights)[0]

    descriptions = {
        'Clear': 'clear sky',
        'Clouds': random.choice(['few clouds', 'scattered clouds', 'broken clouds', 'overcast clouds']),
        'Rain': random.choice(['light rain', 'moderate rain', 'heavy intensity rain']),
        'Drizzle': 'light intensity drizzle',
        'Thunderstorm': 'thunderstorm with rain',
        'Snow': 'light snow',
        'Mist': 'mist',
    }

    return {
        'timestamp': now,
        'temperature': round(temperature, 2),
        'feels_like': round(feels_like, 2),
        'humidity': random.randint(40, 90),
        'pressure': random.randint(980, 1030),
        'wind_speed': round(random.uniform(0, 15), 2),
        'wind_direction': random.randint(0, 359),
        'cloudiness': random.randint(0, 100),
        'weather_condition': condition,
        'weather_description': descriptions[condition],
        'visibility': random.randint(5000, 10000),
    }


def generate_forecast(city: City, days: int = 7) -> list[dict[str, Any]]:
    """Generate weather forecast for the next N days."""
    forecasts = []
    today = date.today()

    for day_offset in range(1, days + 1):
        forecast_date = today + timedelta(days=day_offset)
        month = forecast_date.month

        base_temp = _get_base_temperature(city.latitude, month)
        temp_variation = random.uniform(-8, 8)

        temp_min = base_temp + temp_variation - random.uniform(2, 5)
        temp_max = base_temp + temp_variation + random.uniform(2, 5)
        temp_avg = (temp_min + temp_max) / 2

        conditions = ['Clear', 'Clouds', 'Rain', 'Drizzle', 'Thunderstorm', 'Snow']
        weights = [35, 30, 15, 10, 5, 5]
        condition = random.choices(conditions, weights=weights)[0]

        descriptions = {
            'Clear': 'clear sky',
            'Clouds': 'scattered clouds',
            'Rain': 'moderate rain',
            'Drizzle': 'light drizzle',
            'Thunderstorm': 'thunderstorm',
            'Snow': 'light snow',
        }

        precipitation_prob = {
            'Clear': random.randint(0, 10),
            'Clouds': random.randint(10, 30),
            'Rain': random.randint(60, 90),
            'Drizzle': random.randint(40, 60),
            'Thunderstorm': random.randint(70, 95),
            'Snow': random.randint(50, 80),
        }

        forecasts.append({
            'forecast_date': forecast_date,
            'temperature_min': round(temp_min, 2),
            'temperature_max': round(temp_max, 2),
            'temperature_avg': round(temp_avg, 2),
            'humidity': random.randint(40, 90),
            'pressure': random.randint(980, 1030),
            'wind_speed': round(random.uniform(0, 15), 2),
            'wind_direction': random.randint(0, 359),
            'cloudiness': random.randint(0, 100),
            'weather_condition': condition,
            'weather_description': descriptions[condition],
            'precipitation_probability': precipitation_prob[condition],
        })

    return forecasts


def generate_alert(city: City) -> dict[str, Any] | None:
    """Generate a weather alert if conditions warrant it."""
    # 20% chance of having an alert
    if random.random() > 0.2:
        return None

    alert_types = [
        ('Heat Wave', 'extreme'),
        ('Heavy Rain', 'severe'),
        ('Strong Wind', 'moderate'),
        ('Fog', 'minor'),
        ('Cold Wave', 'severe'),
    ]

    alert_type, severity = random.choice(alert_types)

    titles = {
        'Heat Wave': 'Extreme Heat Warning',
        'Heavy Rain': 'Heavy Rainfall Advisory',
        'Strong Wind': 'Wind Advisory',
        'Fog': 'Dense Fog Advisory',
        'Cold Wave': 'Cold Weather Alert',
    }

    descriptions = {
        'Heat Wave': f'Temperatures are expected to exceed 35°C in {city.name}. Stay hydrated and avoid prolonged sun exposure.',
        'Heavy Rain': f'Heavy rainfall expected in {city.name} with accumulations up to 50mm. Possible flooding in low-lying areas.',
        'Strong Wind': f'Strong winds expected in {city.name} with gusts up to 60 km/h. Secure loose objects.',
        'Fog': f'Dense fog reducing visibility below 200m in {city.name}. Drive carefully.',
        'Cold Wave': f'Temperatures are expected to drop below freezing in {city.name}. Protect pipes and vulnerable individuals.',
    }

    now = timezone.now()
    start_time = now + timedelta(hours=random.randint(1, 12))
    end_time = start_time + timedelta(hours=random.randint(6, 48))

    return {
        'alert_type': alert_type,
        'severity': severity,
        'title': titles[alert_type],
        'description': descriptions[alert_type],
        'start_time': start_time,
        'end_time': end_time,
        'is_active': True,
    }
