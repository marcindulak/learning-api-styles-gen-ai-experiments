"""Weather models."""
import uuid
from datetime import datetime
from typing import Any

from django.contrib.auth.models import User
from django.db import models


class City(models.Model):
    """City model representing a location for weather data."""

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    timezone = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'cities'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['country']),
        ]

    def __str__(self) -> str:
        return f"{self.name}, {self.country}"


class WeatherRecord(models.Model):
    """Current weather record for a city."""

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='weather_records')
    timestamp = models.DateTimeField()
    temperature = models.FloatField(help_text='Temperature in Celsius')
    feels_like = models.FloatField(help_text='Feels like temperature in Celsius')
    humidity = models.IntegerField(help_text='Humidity percentage')
    pressure = models.IntegerField(help_text='Atmospheric pressure in hPa')
    wind_speed = models.FloatField(help_text='Wind speed in m/s')
    wind_direction = models.IntegerField(help_text='Wind direction in degrees')
    cloudiness = models.IntegerField(help_text='Cloudiness percentage')
    weather_condition = models.CharField(max_length=100)
    weather_description = models.CharField(max_length=200)
    visibility = models.IntegerField(help_text='Visibility in meters', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['city', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]

    def __str__(self) -> str:
        return f"{self.city.name} - {self.timestamp} - {self.temperature}°C"


class WeatherForecast(models.Model):
    """Weather forecast for a city (up to 7 days)."""

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='forecasts')
    forecast_date = models.DateField()
    temperature_min = models.FloatField(help_text='Minimum temperature in Celsius')
    temperature_max = models.FloatField(help_text='Maximum temperature in Celsius')
    temperature_avg = models.FloatField(help_text='Average temperature in Celsius')
    humidity = models.IntegerField(help_text='Humidity percentage')
    pressure = models.IntegerField(help_text='Atmospheric pressure in hPa')
    wind_speed = models.FloatField(help_text='Wind speed in m/s')
    wind_direction = models.IntegerField(help_text='Wind direction in degrees')
    cloudiness = models.IntegerField(help_text='Cloudiness percentage')
    weather_condition = models.CharField(max_length=100)
    weather_description = models.CharField(max_length=200)
    precipitation_probability = models.IntegerField(help_text='Probability of precipitation as percentage')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['city', 'forecast_date']
        unique_together = ['city', 'forecast_date']
        indexes = [
            models.Index(fields=['city', 'forecast_date']),
            models.Index(fields=['forecast_date']),
        ]

    def __str__(self) -> str:
        return f"{self.city.name} - {self.forecast_date}"


class WeatherAlert(models.Model):
    """Weather alert for a city."""

    SEVERITY_CHOICES = [
        ('info', 'Information'),
        ('minor', 'Minor'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
        ('extreme', 'Extreme'),
    ]

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-severity', '-start_time']
        indexes = [
            models.Index(fields=['city', 'is_active']),
            models.Index(fields=['-start_time']),
        ]

    def __str__(self) -> str:
        return f"{self.city.name} - {self.alert_type} ({self.severity})"


class WebhookEvent(models.Model):
    """GitHub webhook event."""

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    signature = models.CharField(max_length=200)
    delivery_id = models.CharField(max_length=200, unique=True)
    received_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-received_at']
        indexes = [
            models.Index(fields=['-received_at']),
            models.Index(fields=['processed']),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} - {self.delivery_id}"
