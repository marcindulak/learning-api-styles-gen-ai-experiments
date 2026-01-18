from rest_framework import serializers
from .models import Weather, Forecast
from apps.cities.serializers import CitySerializer


class WeatherSerializer(serializers.ModelSerializer):
    """
    Serializer for Weather model.
    Provides conversion between Weather instances and JSON representations.
    """
    city = CitySerializer(read_only=True)

    class Meta:
        model = Weather
        fields = ('uuid', 'city', 'temperature', 'humidity', 'wind_speed', 'pressure', 'description', 'timestamp', 'created_at', 'updated_at')
        read_only_fields = ('uuid', 'created_at', 'updated_at')


class WeatherDetailSerializer(WeatherSerializer):
    """
    Detailed serializer for Weather model with nested city information.
    """
    pass


class ForecastSerializer(serializers.ModelSerializer):
    """
    Serializer for Forecast model.
    Provides conversion between Forecast instances and JSON representations.
    """
    city = CitySerializer(read_only=True)

    class Meta:
        model = Forecast
        fields = ('uuid', 'city', 'temperature', 'humidity', 'wind_speed', 'pressure', 'description', 'forecast_date', 'created_at', 'updated_at')
        read_only_fields = ('uuid', 'created_at', 'updated_at')
