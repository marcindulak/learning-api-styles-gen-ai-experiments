"""
Models for weather data.
"""
from django.db import models


class City(models.Model):
    """City model for storing city information."""
    uuid = models.UUIDField(primary_key=True, default=models.UUIDField().default, editable=False)
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    region = models.CharField(max_length=200, blank=True)
    timezone = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'cities'

    def __str__(self):
        return self.name
