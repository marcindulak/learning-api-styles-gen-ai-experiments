import uuid
from django.db import models
from apps.cities.models import City


class WeatherForecast(models.Model):
    """
    Model representing a weather forecast for a city on a specific date.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='forecasts')
    forecast_date = models.DateField()
    temperature = models.FloatField(help_text="Temperature in Celsius")
    humidity = models.FloatField(help_text="Humidity percentage")
    wind_speed = models.FloatField(help_text="Wind speed in meters per second")
    condition = models.CharField(max_length=255, help_text="Weather condition description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['forecast_date']
        unique_together = ['city', 'forecast_date']
        indexes = [
            models.Index(fields=['city', 'forecast_date']),
        ]

    def __str__(self):
        return f"{self.city.name} - {self.forecast_date}: {self.condition}"
