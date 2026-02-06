from rest_framework import serializers

from weather_service.models import City, WeatherForecast, WeatherRecord


class CitySerializer(serializers.ModelSerializer):
    """
    Serializer for City model.
    """

    class Meta:
        model = City
        fields = ["uuid", "name", "country", "region", "timezone", "latitude", "longitude"]
        read_only_fields = ["uuid"]


class WeatherRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for WeatherRecord model.
    """

    city_name = serializers.CharField(source="city.name", read_only=True)

    class Meta:
        model = WeatherRecord
        fields = [
            "id",
            "city",
            "city_name",
            "timestamp",
            "temperature",
            "humidity",
            "pressure",
            "wind_speed",
            "precipitation",
        ]
        read_only_fields = ["id", "timestamp", "city_name"]


class WeatherForecastSerializer(serializers.ModelSerializer):
    """
    Serializer for WeatherForecast model.
    """

    city_name = serializers.CharField(source="city.name", read_only=True)

    class Meta:
        model = WeatherForecast
        fields = [
            "id",
            "city",
            "city_name",
            "forecast_date",
            "temperature",
            "humidity",
            "pressure",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "city_name"]
