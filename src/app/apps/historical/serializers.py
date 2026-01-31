from rest_framework import serializers
from .models import WeatherHistory


class WeatherHistorySerializer(serializers.ModelSerializer):
    """Serializer for WeatherHistory model."""
    city_uuid = serializers.UUIDField(source='city.uuid', read_only=True)
    city_name = serializers.CharField(source='city.name', read_only=True)

    class Meta:
        model = WeatherHistory
        fields = [
            'uuid',
            'city_uuid',
            'city_name',
            'date',
            'temperature',
            'humidity',
            'wind_speed',
            'condition',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']


class WeatherHistoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating WeatherHistory records."""
    date = serializers.DateField()
    temperature = serializers.FloatField()
    humidity = serializers.FloatField()
    wind_speed = serializers.FloatField()
    condition = serializers.CharField(max_length=255)

    class Meta:
        model = WeatherHistory
        fields = [
            'date',
            'temperature',
            'humidity',
            'wind_speed',
            'condition',
        ]
