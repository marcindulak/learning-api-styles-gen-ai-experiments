"""DRF serializers for the Weather Forecast Service."""

from datetime import date, timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import City, WeatherAlert, WeatherForecast, WeatherRecord


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = [
            "uuid",
            "name",
            "country",
            "region",
            "timezone",
            "latitude",
            "longitude",
        ]
        read_only_fields = ["uuid"]


class WeatherRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherRecord
        fields = [
            "uuid",
            "city",
            "timestamp",
            "temperature",
            "feels_like",
            "humidity",
            "pressure",
            "wind_speed",
            "wind_direction",
            "precipitation",
            "visibility",
            "uv_index",
            "cloud_cover",
            "description",
            "created_at",
        ]
        read_only_fields = ["uuid", "city", "created_at"]

    def validate_timestamp(self, value):
        max_future = timezone.now() + timedelta(days=7)
        if value > max_future:
            raise serializers.ValidationError(
                "Timestamp must not be more than 7 days in the future."
            )
        return value


class WeatherForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherForecast
        fields = [
            "uuid",
            "city",
            "forecast_date",
            "temperature_high",
            "temperature_low",
            "humidity",
            "precipitation_prob",
            "wind_speed",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uuid", "city", "created_at", "updated_at"]

    def validate_forecast_date(self, value):
        max_date = date.today() + timedelta(days=7)
        if value > max_date:
            raise serializers.ValidationError(
                "Forecast date must be within 7 days."
            )
        return value

    def validate(self, data):
        high = data.get("temperature_high")
        low = data.get("temperature_low")
        if high is not None and low is not None and high < low:
            raise serializers.ValidationError(
                {"temperature_high": "High temperature must be >= low temperature."}
            )
        return data


class WeatherAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherAlert
        fields = [
            "uuid",
            "city",
            "severity",
            "event",
            "description",
            "starts_at",
            "expires_at",
            "active",
            "created_at",
        ]
        read_only_fields = ["uuid", "created_at"]

    def validate(self, data):
        starts_at = data.get("starts_at")
        expires_at = data.get("expires_at")
        if starts_at and expires_at and expires_at <= starts_at:
            raise serializers.ValidationError(
                {"expires_at": "Expiry time must be after start time."}
            )
        return data
