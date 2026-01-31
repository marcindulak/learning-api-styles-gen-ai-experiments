import uuid
from django.db import models
from apps.cities.models import City


class CurrentWeather(models.Model):
    """
    Model representing current weather data for a city.
    Stores the latest weather indicators.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='current_weather')
    temperature = models.FloatField(help_text="Temperature in Celsius")
    humidity = models.FloatField(help_text="Humidity percentage")
    wind_speed = models.FloatField(help_text="Wind speed in meters per second")
    pressure = models.FloatField(help_text="Atmospheric pressure in hPa")
    condition_code = models.CharField(max_length=50, help_text="Weather condition code")
    condition = models.CharField(max_length=255, help_text="Weather condition description")
    timestamp = models.DateTimeField(help_text="Measurement timestamp")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['city', 'timestamp']),
        ]
        verbose_name = 'Current Weather'
        verbose_name_plural = 'Current Weather'

    def __str__(self):
        return f"{self.city.name} - {self.timestamp}: {self.condition}"
