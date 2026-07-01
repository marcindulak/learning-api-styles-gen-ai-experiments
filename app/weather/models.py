"""Domain models of the Weather Forecast Service."""
import uuid

from django.db import models


class City(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    timezone = models.CharField(max_length=64)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        verbose_name_plural = "cities"

    def __str__(self):
        return self.name


class WeatherRecord(models.Model):
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name="weather_records"
    )
    observed_at = models.DateTimeField()
    temperature = models.FloatField(help_text="Air temperature in degrees Celsius")
    humidity = models.FloatField(help_text="Relative humidity in percent")
    wind_speed = models.FloatField(help_text="Wind speed in meters per second")
    pressure = models.FloatField(help_text="Atmospheric pressure in hectopascals")
    precipitation = models.FloatField(help_text="Precipitation in millimeters")
    source = models.CharField(max_length=200, blank=True, default="")

    class Meta:
        ordering = ["observed_at"]

    def __str__(self):
        return f"{self.city.name} at {self.observed_at:%Y-%m-%d %H:%M}"
