import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone

# FR-007: a reading is stale once more than this long has passed since it
# was last refreshed from the weather data provider.
STALE_AFTER = timedelta(hours=1)


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
    # FR-007: identifies the weather data provider a reading came from
    # (e.g. "open-meteo"), so consumers can be certain no value is fabricated.
    source = models.CharField(max_length=100)
    # editable=False keeps this out of ModelForms (e.g. the CMS admin form),
    # matching auto_now_add's implicit behavior; default=timezone.now (instead
    # of auto_now_add=True) allows FR-005 to still set it explicitly via the
    # ORM for backfilled historical records.
    recorded_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        get_latest_by = "recorded_at"

    def __str__(self) -> str:
        return f"{self.city} @ {self.recorded_at}: {self.temperature}"

    @property
    def is_stale(self) -> bool:
        return timezone.now() - self.recorded_at > STALE_AFTER


class Forecast(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="forecasts")
    date = models.DateField()
    condition = models.CharField(max_length=100)
    temp_min = models.FloatField()
    temp_max = models.FloatField()

    class Meta:
        ordering = ["date"]
        unique_together = ("city", "date")

    def __str__(self) -> str:
        return f"{self.city} @ {self.date}: {self.condition}"
