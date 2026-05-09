"""Serializers for the cities REST API."""

from __future__ import annotations

from rest_framework import serializers

from .models import City


class CitySerializer(serializers.ModelSerializer):
    """Maps :class:`City` rows to and from JSON for the REST API."""

    class Meta:
        model = City
        fields = (
            "uuid",
            "name",
            "country",
            "region",
            "timezone",
            "latitude",
            "longitude",
        )
        read_only_fields = ("uuid",)
