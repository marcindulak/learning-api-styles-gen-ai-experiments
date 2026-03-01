"""Weather serializers."""
from rest_framework import serializers

from .models import City, WeatherAlert, WeatherForecast, WeatherRecord


class CitySerializer(serializers.ModelSerializer):
    """City serializer."""

    class Meta:
        model = City
        fields = ['uuid', 'name', 'country', 'region', 'timezone', 'latitude', 'longitude', 'created_at', 'updated_at']
        read_only_fields = ['uuid', 'created_at', 'updated_at']


class WeatherRecordSerializer(serializers.ModelSerializer):
    """Weather record serializer."""

    city = CitySerializer(read_only=True)
    city_uuid = serializers.UUIDField(write_only=True, source='city_id')

    class Meta:
        model = WeatherRecord
        fields = [
            'uuid', 'city', 'city_uuid', 'timestamp',
            'temperature', 'feels_like', 'humidity', 'pressure',
            'wind_speed', 'wind_direction', 'cloudiness',
            'weather_condition', 'weather_description', 'visibility',
            'created_at'
        ]
        read_only_fields = ['uuid', 'created_at']


class WeatherForecastSerializer(serializers.ModelSerializer):
    """Weather forecast serializer."""

    city = CitySerializer(read_only=True)
    city_uuid = serializers.UUIDField(write_only=True, source='city_id')

    class Meta:
        model = WeatherForecast
        fields = [
            'uuid', 'city', 'city_uuid', 'forecast_date',
            'temperature_min', 'temperature_max', 'temperature_avg',
            'humidity', 'pressure', 'wind_speed', 'wind_direction',
            'cloudiness', 'weather_condition', 'weather_description',
            'precipitation_probability', 'created_at', 'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']


class WeatherAlertSerializer(serializers.ModelSerializer):
    """Weather alert serializer."""

    city = CitySerializer(read_only=True)
    city_uuid = serializers.UUIDField(write_only=True, source='city_id')

    class Meta:
        model = WeatherAlert
        fields = [
            'uuid', 'city', 'city_uuid', 'alert_type', 'severity',
            'title', 'description', 'start_time', 'end_time',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']
