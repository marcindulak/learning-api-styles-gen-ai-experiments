from rest_framework import serializers
from .models import City, WeatherRecord, WeatherForecast, WeatherAlert


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = [
            "uuid", "name", "country", "region",
            "timezone", "latitude", "longitude",
            "created_at", "updated_at",
        ]
        read_only_fields = ["uuid", "created_at", "updated_at"]


class WeatherRecordSerializer(serializers.ModelSerializer):
    city_uuid = serializers.UUIDField(source="city.uuid", read_only=True)
    city_name = serializers.CharField(source="city.name", read_only=True)

    class Meta:
        model = WeatherRecord
        fields = [
            "uuid", "city", "city_uuid", "city_name", "recorded_at",
            "temperature_celsius", "humidity_percent", "wind_speed_kmh",
            "precipitation_mm", "description", "created_at",
        ]
        read_only_fields = ["uuid", "city_uuid", "city_name", "created_at"]


class WeatherForecastSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source="city.name", read_only=True)

    class Meta:
        model = WeatherForecast
        fields = [
            "uuid", "city", "city_name", "forecast_date",
            "temperature_max_celsius", "temperature_min_celsius",
            "precipitation_mm", "wind_speed_kmh", "description",
            "created_at", "updated_at",
        ]
        read_only_fields = ["uuid", "city_name", "created_at", "updated_at"]

    def validate(self, data):
        from datetime import date, timedelta
        if "forecast_date" in data:
            max_date = date.today() + timedelta(days=WeatherForecast.max_days())
            if data["forecast_date"] > max_date:
                raise serializers.ValidationError(
                    {"forecast_date": f"Forecast cannot exceed {WeatherForecast.max_days()} days from today."}
                )
        return data


class WeatherAlertSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source="city.name", read_only=True)

    class Meta:
        model = WeatherAlert
        fields = [
            "uuid", "city", "city_name", "severity", "title", "message",
            "issued_at", "expires_at", "created_by",
        ]
        read_only_fields = ["uuid", "city_name", "created_by"]
