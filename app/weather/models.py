"""
Models for weather data.
"""
import uuid
from django.db import models


class City(models.Model):
    """City model for storing city information."""
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    region = models.CharField(max_length=200, blank=True)
    timezone = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'cities'

    def __str__(self):
        return self.name


class CurrentWeather(models.Model):
    """Current weather data for a city."""
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='current_weather')
    temperature = models.FloatField()
    humidity = models.FloatField()
    pressure = models.FloatField()
    wind_speed = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'current weather'

    def __str__(self):
        return f"{self.city.name} - {self.timestamp}"


class WeatherForecast(models.Model):
    """Weather forecast data for a city."""
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='forecasts')
    forecast_date = models.DateField()
    temperature = models.FloatField()
    humidity = models.FloatField()
    pressure = models.FloatField()
    wind_speed = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['forecast_date']
        unique_together = ['city', 'forecast_date']

    def __str__(self):
        return f"{self.city.name} - {self.forecast_date}"
