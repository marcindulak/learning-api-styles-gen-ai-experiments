import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class City(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    timezone = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "cities"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}, {self.country}"


class WeatherRecord(models.Model):
    """Actual historical weather data for a city."""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="weather_records")
    recorded_at = models.DateTimeField()
    temperature_celsius = models.FloatField()
    humidity_percent = models.FloatField()
    wind_speed_kmh = models.FloatField()
    precipitation_mm = models.FloatField(default=0.0)
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"{self.city.name} @ {self.recorded_at}: {self.temperature_celsius}°C"


class WeatherForecast(models.Model):
    """Up to 7-day weather forecast for a city."""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="forecasts")
    forecast_date = models.DateField()
    temperature_max_celsius = models.FloatField()
    temperature_min_celsius = models.FloatField()
    precipitation_mm = models.FloatField(default=0.0)
    wind_speed_kmh = models.FloatField()
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["forecast_date"]
        unique_together = [["city", "forecast_date"]]

    def __str__(self):
        return f"{self.city.name} forecast {self.forecast_date}"

    @classmethod
    def max_days(cls):
        return 7


class WeatherAlert(models.Model):
    """Weather alert broadcast via WebSocket."""
    SEVERITY_CHOICES = [
        ("info", "Info"),
        ("warning", "Warning"),
        ("severe", "Severe"),
        ("extreme", "Extreme"),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="alerts")
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    issued_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="alerts"
    )

    class Meta:
        ordering = ["-issued_at"]

    def __str__(self):
        return f"[{self.severity.upper()}] {self.city.name}: {self.title}"
