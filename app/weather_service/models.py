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
