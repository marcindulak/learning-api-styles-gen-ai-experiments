from rest_framework import serializers

from weather.models import City, WeatherRecord


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


class WeatherRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherRecord
        fields = [
            "observed_at",
            "temperature",
            "humidity",
            "wind_speed",
            "pressure",
            "precipitation",
            "source",
        ]
