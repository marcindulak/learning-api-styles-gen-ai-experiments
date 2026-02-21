from datetime import date, timedelta
from rest_framework import serializers
from .models import City, WeatherRecord, Forecast


class CitySerializer(serializers.ModelSerializer):
    """Serializer for City model."""

    class Meta:
        model = City
        fields = ['uuid', 'name', 'country', 'region', 'timezone', 'latitude', 'longitude', 'created_at', 'updated_at']
        read_only_fields = ['uuid', 'created_at', 'updated_at']


class WeatherRecordSerializer(serializers.ModelSerializer):
    """Serializer for WeatherRecord model."""

    class Meta:
        model = WeatherRecord
        fields = [
            'uuid', 'city', 'recorded_at', 'temperature', 'feels_like', 'humidity',
            'wind_speed', 'wind_direction', 'pressure', 'precipitation',
            'uv_index', 'visibility', 'cloud_cover', 'description'
        ]
        read_only_fields = ['uuid']


class ForecastSerializer(serializers.ModelSerializer):
    """Serializer for Forecast model with 7-day validation."""

    class Meta:
        model = Forecast
        fields = [
            'uuid', 'city', 'forecast_date', 'temperature_high', 'temperature_low',
            'humidity', 'wind_speed', 'precipitation_probability', 'description', 'created_at'
        ]
        read_only_fields = ['uuid', 'created_at']

    def validate_forecast_date(self, value):
        """
        Validate that forecast_date is not more than 7 days from today.
        This explicit serializer-level validation ensures DRF enforces the limit,
        since DRF does not automatically call model.full_clean().
        """
        if value:
            max_date = date.today() + timedelta(days=7)
            if value > max_date:
                raise serializers.ValidationError(
                    f'Forecast date cannot be more than 7 days from today (max: {max_date})'
                )
        return value
