from rest_framework import serializers

from .models import WeatherRecord


class WeatherRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherRecord
        fields = ["temperature", "humidity", "wind_speed", "precipitation_probability", "condition"]
