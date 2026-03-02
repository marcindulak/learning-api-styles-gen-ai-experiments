from datetime import date, timedelta

from rest_framework import serializers

from src.weather.models import City, CurrentWeather, WeatherAlert, WeatherForecast


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['uuid', 'name', 'country', 'region', 'timezone', 'latitude', 'longitude', 'created_at', 'updated_at']
        read_only_fields = ['uuid', 'created_at', 'updated_at']


class CurrentWeatherSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(write_only=True)

    class Meta:
        model = CurrentWeather
        fields = ['uuid', 'city_name', 'temperature', 'humidity', 'pressure', 'wind_speed', 'conditions', 'timestamp', 'created_at']
        read_only_fields = ['uuid', 'created_at']

    def create(self, validated_data: dict) -> CurrentWeather:
        city_name = validated_data.pop('city_name')
        city = City.objects.get(name=city_name)
        validated_data['city'] = city
        return super().create(validated_data)

    def to_representation(self, instance: CurrentWeather) -> dict:
        representation = super().to_representation(instance)
        representation['city_name'] = instance.city.name
        return representation


class WeatherForecastSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(write_only=True)

    class Meta:
        model = WeatherForecast
        fields = ['uuid', 'city_name', 'forecast_date', 'temperature', 'humidity', 'pressure', 'wind_speed', 'conditions', 'created_at']
        read_only_fields = ['uuid', 'created_at']

    def validate(self, attrs: dict) -> dict:
        forecast_date = attrs.get('forecast_date')
        if forecast_date:
            max_forecast_date = date.today() + timedelta(days=7)
            if forecast_date > max_forecast_date:
                raise serializers.ValidationError({'forecast_date': 'Forecast date cannot be more than 7 days in the future'})
        return attrs

    def create(self, validated_data: dict) -> WeatherForecast:
        city_name = validated_data.pop('city_name')
        city = City.objects.get(name=city_name)
        validated_data['city'] = city
        return super().create(validated_data)

    def to_representation(self, instance: WeatherForecast) -> dict:
        representation = super().to_representation(instance)
        representation['city_name'] = instance.city.name
        return representation


class WeatherAlertSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(write_only=True)

    class Meta:
        model = WeatherAlert
        fields = ['uuid', 'city_name', 'severity', 'message', 'created_at']
        read_only_fields = ['uuid', 'created_at']

    def create(self, validated_data: dict) -> WeatherAlert:
        city_name = validated_data.pop('city_name')
        city = City.objects.get(name=city_name)
        validated_data['city'] = city
        return super().create(validated_data)

    def to_representation(self, instance: WeatherAlert) -> dict:
        representation = super().to_representation(instance)
        representation['city_name'] = instance.city.name
        return representation
