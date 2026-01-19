import uuid
from django.db import models
from apps.cities.models import City


class Weather(models.Model):
    """
    Model representing weather data for a city at a specific timestamp.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='weather_records')
    temperature = models.FloatField()
    humidity = models.IntegerField()
    wind_speed = models.FloatField()
    pressure = models.FloatField(null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['city', '-timestamp']),
        ]

    def __str__(self):
        return f"Weather for {self.city.name} at {self.timestamp}"


class Forecast(models.Model):
    """
    Model representing weather forecast data for a city on a specific date.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='forecasts')
    temperature = models.FloatField()
    humidity = models.IntegerField()
    wind_speed = models.FloatField()
    pressure = models.FloatField(null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    forecast_date = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['forecast_date']
        indexes = [
            models.Index(fields=['city', 'forecast_date']),
        ]

    def __str__(self):
        return f"Forecast for {self.city.name} on {self.forecast_date.date()}"
