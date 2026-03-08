"""
Serializers for weather data models.
"""
from rest_framework import serializers
from weather.models import City


class CitySerializer(serializers.ModelSerializer):
    """Serializer for City model."""

    class Meta:
        model = City
        fields = [
            'uuid',
            'name',
            'country',
            'region',
            'timezone',
            'latitude',
            'longitude',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']
