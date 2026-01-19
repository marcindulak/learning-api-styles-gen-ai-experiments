import uuid
from django.db import models


class City(models.Model):
    """
    Model representing a city where weather data is tracked.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    timezone = models.CharField(max_length=63)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return f"{self.name}, {self.country}"
