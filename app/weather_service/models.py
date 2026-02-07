import uuid

from django.db import models


class City(models.Model):
    """
    Model representing a city in the weather forecast service.
    Weather data is limited to the 5 biggest cities in the world.
    """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=50)
    timezone = models.CharField(max_length=50)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    class Meta:
        verbose_name_plural = "cities"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name}, {self.country}"


class WeatherRecord(models.Model):
    """
    Model representing a weather record for a city.
    Contains common weather indicators including temperature, humidity, pressure,
    wind speed, and precipitation.
    """

    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="weather_records")
    timestamp = models.DateTimeField(auto_now_add=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, help_text="Temperature in Celsius")
    humidity = models.IntegerField(help_text="Humidity percentage (0-100)")
    pressure = models.IntegerField(help_text="Atmospheric pressure in hPa")
    wind_speed = models.DecimalField(max_digits=5, decimal_places=2, help_text="Wind speed in km/h")
    precipitation = models.DecimalField(max_digits=5, decimal_places=2, help_text="Precipitation in mm")

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return f"{self.city.name} - {self.timestamp}"


class WeatherForecast(models.Model):
    """
    Model representing a weather forecast for a city.
    Forecasts are limited to a maximum of 7 days.
    """

    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="forecasts")
    forecast_date = models.DateField(help_text="Date for which the forecast is made")
    temperature = models.DecimalField(max_digits=5, decimal_places=2, help_text="Forecasted temperature in Celsius")
    humidity = models.IntegerField(help_text="Forecasted humidity percentage (0-100)")
    pressure = models.IntegerField(help_text="Forecasted atmospheric pressure in hPa")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["forecast_date"]
        unique_together = ["city", "forecast_date"]

    def __str__(self) -> str:
        return f"{self.city.name} - {self.forecast_date}"
