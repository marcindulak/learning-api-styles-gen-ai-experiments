from datetime import date, timedelta
from typing import Optional

import graphene
from graphene_django import DjangoObjectType

from src.weather.models import City, CurrentWeather, WeatherForecast


class CityType(DjangoObjectType):
    class Meta:
        model = City
        fields = ('uuid', 'name', 'country', 'region', 'timezone', 'latitude', 'longitude')


class CurrentWeatherType(DjangoObjectType):
    city_name = graphene.String()

    class Meta:
        model = CurrentWeather
        fields = ('uuid', 'temperature', 'humidity', 'pressure', 'wind_speed', 'conditions', 'timestamp')

    def resolve_city_name(self, info) -> str:
        return self.city.name


class WeatherForecastType(DjangoObjectType):
    city_name = graphene.String()

    class Meta:
        model = WeatherForecast
        fields = ('uuid', 'forecast_date', 'temperature', 'humidity', 'pressure', 'wind_speed', 'conditions')

    def resolve_city_name(self, info) -> str:
        return self.city.name


class Query(graphene.ObjectType):
    current_weather = graphene.Field(CurrentWeatherType, city_name=graphene.String(required=True))
    forecast = graphene.List(WeatherForecastType, city_name=graphene.String(required=True), days=graphene.Int())

    def resolve_current_weather(self, info, city_name: str) -> Optional[CurrentWeather]:
        try:
            city = City.objects.get(name=city_name)
            return CurrentWeather.objects.filter(city=city).first()
        except City.DoesNotExist:
            return None

    def resolve_forecast(self, info, city_name: str, days: Optional[int] = None) -> list[WeatherForecast]:
        try:
            city = City.objects.get(name=city_name)
            queryset = WeatherForecast.objects.filter(city=city)
            if days is not None:
                max_date = date.today() + timedelta(days=days)
                queryset = queryset.filter(forecast_date__lte=max_date)
            return list(queryset)
        except City.DoesNotExist:
            return []


schema = graphene.Schema(query=Query)
