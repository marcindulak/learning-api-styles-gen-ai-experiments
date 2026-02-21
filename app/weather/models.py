import uuid
from datetime import date, timedelta
from django.db import models
from django.core.exceptions import ValidationError


class City(models.Model):
    """City model for weather data locations."""
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    timezone = models.CharField(max_length=50)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Cities'
        constraints = [
            models.UniqueConstraint(fields=['name', 'country'], name='unique_city_name_country')
        ]

    def __str__(self):
        return f"{self.name}, {self.country}"


class WeatherRecord(models.Model):
    """Historical weather data records."""
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='weather_records')
    recorded_at = models.DateTimeField()
    temperature = models.DecimalField(max_digits=5, decimal_places=2, help_text="Temperature in Celsius")
    feels_like = models.DecimalField(max_digits=5, decimal_places=2, help_text="Feels like temperature in Celsius")
    humidity = models.DecimalField(max_digits=5, decimal_places=2, help_text="Humidity percentage")
    wind_speed = models.DecimalField(max_digits=5, decimal_places=2, help_text="Wind speed in km/h")
    wind_direction = models.DecimalField(max_digits=5, decimal_places=2, help_text="Wind direction in degrees")
    pressure = models.DecimalField(max_digits=7, decimal_places=2, help_text="Atmospheric pressure in hPa")
    precipitation = models.DecimalField(max_digits=5, decimal_places=2, help_text="Precipitation in mm")
    uv_index = models.DecimalField(max_digits=4, decimal_places=1, help_text="UV index")
    visibility = models.DecimalField(max_digits=6, decimal_places=2, help_text="Visibility in km")
    cloud_cover = models.DecimalField(max_digits=5, decimal_places=2, help_text="Cloud cover percentage")
    description = models.CharField(max_length=200)

    class Meta:
        indexes = [
            models.Index(fields=['city', 'recorded_at']),
        ]
        ordering = ['-recorded_at']

    def __str__(self):
        return f"{self.city.name} - {self.recorded_at.strftime('%Y-%m-%d %H:%M')} - {self.temperature}°C"


class Forecast(models.Model):
    """Weather forecast data (up to 7 days ahead)."""
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='forecasts')
    forecast_date = models.DateField()
    temperature_high = models.DecimalField(max_digits=5, decimal_places=2, help_text="High temperature in Celsius")
    temperature_low = models.DecimalField(max_digits=5, decimal_places=2, help_text="Low temperature in Celsius")
    humidity = models.DecimalField(max_digits=5, decimal_places=2, help_text="Humidity percentage")
    wind_speed = models.DecimalField(max_digits=5, decimal_places=2, help_text="Wind speed in km/h")
    precipitation_probability = models.DecimalField(max_digits=5, decimal_places=2, help_text="Precipitation probability percentage")
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['city', 'forecast_date'], name='unique_city_forecast_date')
        ]
        ordering = ['forecast_date']

    def clean(self):
        """Validate that forecast_date is not more than 7 days from today."""
        super().clean()
        if self.forecast_date:
            max_date = date.today() + timedelta(days=7)
            if self.forecast_date > max_date:
                raise ValidationError({
                    'forecast_date': f'Forecast date cannot be more than 7 days from today (max: {max_date})'
                })

    def save(self, *args, **kwargs):
        """Override save to call full_clean for validation."""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.city.name} - {self.forecast_date} - {self.temperature_high}°C/{self.temperature_low}°C"


class WeatherAlert(models.Model):
    """Weather alerts and warnings."""
    ALERT_TYPES = [
        ('storm', 'Storm'),
        ('heat', 'Heat'),
        ('cold', 'Cold'),
        ('flood', 'Flood'),
        ('wind', 'Wind'),
    ]

    SEVERITY_LEVELS = [
        ('advisory', 'Advisory'),
        ('watch', 'Watch'),
        ('warning', 'Warning'),
    ]

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    title = models.CharField(max_length=200)
    description = models.TextField()
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-issued_at']

    def __str__(self):
        return f"{self.city.name} - {self.get_alert_type_display()} {self.get_severity_display()} - {self.title}"


class WebhookEvent(models.Model):
    """GitHub webhook events log."""
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=100, help_text="X-GitHub-Event header value")
    payload = models.JSONField()
    received_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-received_at']

    def __str__(self):
        return f"{self.event_type} - {self.received_at.strftime('%Y-%m-%d %H:%M:%S')}"
