from rest_framework import serializers
from .models import WeatherForecast


class WeatherForecastSerializer(serializers.ModelSerializer):
    """Serializer for WeatherForecast model."""
    city_uuid = serializers.UUIDField(source='city.uuid', read_only=True)
    city_name = serializers.CharField(source='city.name', read_only=True)

    class Meta:
        model = WeatherForecast
        fields = [
            'uuid',
            'city_uuid',
            'city_name',
            'forecast_date',
            'temperature',
            'humidity',
            'wind_speed',
            'condition',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']
