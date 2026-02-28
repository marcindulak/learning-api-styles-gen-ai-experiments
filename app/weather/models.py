"""Domain models for the Weather Forecast Service."""

import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class City(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    timezone = models.CharField(max_length=100)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "cities"
        ordering = ["name"]

    def __str__(self):
        return self.name


class WeatherRecord(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="weather_records")
    timestamp = models.DateTimeField(db_index=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=1)
    feels_like = models.DecimalField(max_digits=5, decimal_places=1)
    humidity = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    pressure = models.DecimalField(max_digits=6, decimal_places=1)
    wind_speed = models.DecimalField(max_digits=5, decimal_places=1)
    wind_direction = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(360)]
    )
    precipitation = models.DecimalField(max_digits=5, decimal_places=1, default=0.0)
    visibility = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100000)]
    )
    uv_index = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(15)],
    )
    cloud_cover = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("city", "timestamp")]
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.city.name} @ {self.timestamp}"


class WeatherForecast(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="forecasts")
    forecast_date = models.DateField(db_index=True)
    temperature_high = models.DecimalField(max_digits=5, decimal_places=1)
    temperature_low = models.DecimalField(max_digits=5, decimal_places=1)
    humidity = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    precipitation_prob = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    wind_speed = models.DecimalField(max_digits=5, decimal_places=1)
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("city", "forecast_date")]
        ordering = ["forecast_date"]

    def __str__(self):
        return f"{self.city.name} forecast {self.forecast_date}"


class WeatherAlert(models.Model):
    SEVERITY_CHOICES = [
        ("advisory", "Advisory"),
        ("watch", "Watch"),
        ("warning", "Warning"),
        ("emergency", "Emergency"),
    ]

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="alerts")
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    event = models.CharField(max_length=200)
    description = models.TextField()
    starts_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.city.name} - {self.event} ({self.severity})"
