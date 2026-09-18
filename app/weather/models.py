import uuid

from django.db import models
from django.utils import timezone


class City(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    region = models.CharField(max_length=200)
    timezone = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        verbose_name_plural = "cities"

    def __str__(self) -> str:
        return self.name


class WeatherRecord(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="weather_records")
    temperature = models.FloatField()
    humidity = models.PositiveSmallIntegerField()
    wind_speed = models.FloatField()
    precipitation_probability = models.PositiveSmallIntegerField()
    condition = models.CharField(max_length=100)
    # editable=False keeps this out of ModelForms (e.g. the CMS admin form),
    # matching auto_now_add's implicit behavior; default=timezone.now (instead
    # of auto_now_add=True) allows FR-005 to still set it explicitly via the
    # ORM for backfilled historical records.
    recorded_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        get_latest_by = "recorded_at"

    def __str__(self) -> str:
        return f"{self.city} @ {self.recorded_at}: {self.temperature}"
