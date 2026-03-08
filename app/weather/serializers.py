"""
Serializers for weather data models.
"""
from datetime import date, timedelta
from rest_framework import serializers
from weather.models import City, CurrentWeather, WeatherForecast


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


class CurrentWeatherSerializer(serializers.ModelSerializer):
    """Serializer for CurrentWeather model."""
    city_name = serializers.CharField(write_only=True)

    class Meta:
        model = CurrentWeather
        fields = [
            'id',
            'city',
            'city_name',
            'temperature',
            'humidity',
            'pressure',
            'wind_speed',
            'timestamp'
        ]
        read_only_fields = ['id', 'city', 'timestamp']

    def create(self, validated_data: dict) -> CurrentWeather:
        city_name = validated_data.pop('city_name')
        city = City.objects.get(name=city_name)
        validated_data['city'] = city
        return super().create(validated_data)


class WeatherForecastSerializer(serializers.ModelSerializer):
    """Serializer for WeatherForecast model."""
    city_name = serializers.CharField(write_only=True)

    class Meta:
        model = WeatherForecast
        fields = [
            'id',
            'city',
            'city_name',
            'forecast_date',
            'temperature',
            'humidity',
            'pressure',
            'wind_speed',
            'created_at'
        ]
        read_only_fields = ['id', 'city', 'created_at']

    def validate_forecast_date(self, value: date) -> date:
        """Validate that forecast date is within 7 days from today."""
        max_forecast_date = date.today() + timedelta(days=7)
        if value > max_forecast_date:
            raise serializers.ValidationError(
                f"Forecast date cannot be more than 7 days in the future. "
                f"Maximum allowed date is {max_forecast_date}."
            )
        return value

    def create(self, validated_data: dict) -> WeatherForecast:
        city_name = validated_data.pop('city_name')
        city = City.objects.get(name=city_name)
        validated_data['city'] = city
        return super().create(validated_data)
