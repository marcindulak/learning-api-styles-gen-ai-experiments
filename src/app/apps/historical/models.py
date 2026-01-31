import uuid
from django.db import models
from apps.cities.models import City


class WeatherHistory(models.Model):
    """
    Model representing historical weather data for a city on a specific date.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='historical_weather')
    date = models.DateField()
    temperature = models.FloatField(help_text="Temperature in Celsius")
    humidity = models.FloatField(help_text="Humidity percentage")
    wind_speed = models.FloatField(help_text="Wind speed in meters per second")
    condition = models.CharField(max_length=255, help_text="Weather condition description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['city', 'date']
        indexes = [
            models.Index(fields=['city', 'date']),
        ]
        verbose_name = 'Weather History'
        verbose_name_plural = 'Weather Histories'

    def __str__(self):
        return f"{self.city.name} - {self.date}: {self.condition}"
