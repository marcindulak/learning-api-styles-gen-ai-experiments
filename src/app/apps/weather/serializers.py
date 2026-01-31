from rest_framework import serializers
from .models import CurrentWeather


class CurrentWeatherSerializer(serializers.ModelSerializer):
    """
    Serializer for CurrentWeather model.
    Provides conversion between CurrentWeather instances and JSON representations.
    """
    city_uuid = serializers.UUIDField(source='city.uuid', read_only=True)

    class Meta:
        model = CurrentWeather
        fields = (
            'uuid',
            'city_uuid',
            'temperature',
            'humidity',
            'wind_speed',
            'pressure',
            'condition_code',
            'condition',
            'timestamp',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('uuid', 'city_uuid', 'created_at', 'updated_at')


class CurrentWeatherCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating CurrentWeather records.
    """
    city_uuid = serializers.UUIDField(write_only=True)

    class Meta:
        model = CurrentWeather
        fields = (
            'city_uuid',
            'temperature',
            'humidity',
            'wind_speed',
            'pressure',
            'condition_code',
            'condition',
            'timestamp',
        )

    def create(self, validated_data):
        from apps.cities.models import City
        city_uuid = validated_data.pop('city_uuid')
        city = City.objects.get(uuid=city_uuid)
        return CurrentWeather.objects.create(city=city, **validated_data)
