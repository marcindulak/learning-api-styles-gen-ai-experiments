from django.contrib.auth.models import User
from rest_framework import serializers

from .models import City, Forecast, WeatherRecord

_INDICATOR_FIELDS = ["temperature", "humidity", "wind_speed", "precipitation_probability", "condition"]


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        # City.uuid has editable=False, which ModelSerializer already infers
        # as read_only=True, so no explicit read_only_fields is needed.
        fields = ["uuid", "name", "country", "region", "timezone", "latitude", "longitude"]


class WeatherRecordSerializer(serializers.ModelSerializer):
    # Maps to the WeatherRecord.is_stale property (FR-007), not a model field.
    stale = serializers.BooleanField(source="is_stale", read_only=True)

    class Meta:
        model = WeatherRecord
        fields = _INDICATOR_FIELDS + ["stale"]


class HistoricalWeatherRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherRecord
        fields = _INDICATOR_FIELDS + ["recorded_at"]


class ForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forecast
        fields = ["date", "condition", "temp_min", "temp_max"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username"]
