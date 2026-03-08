"""
GraphQL schema.
"""
from datetime import date, timedelta
from typing import Optional

import graphene
from graphene_django import DjangoObjectType

from .models import City, CurrentWeather, WeatherForecast


class CityType(DjangoObjectType):
    class Meta:
        model = City
        fields = ('uuid', 'name', 'country', 'region', 'timezone', 'latitude', 'longitude')


class CurrentWeatherType(DjangoObjectType):
    class Meta:
        model = CurrentWeather
        fields = ('temperature', 'humidity', 'pressure', 'wind_speed', 'timestamp')


class WeatherForecastType(DjangoObjectType):
    class Meta:
        model = WeatherForecast
        fields = ('forecast_date', 'temperature', 'humidity', 'pressure', 'wind_speed')


class Query(graphene.ObjectType):
    current_weather = graphene.Field(
        CurrentWeatherType,
        city_name=graphene.String(required=True),
    )
    forecasts = graphene.List(
        WeatherForecastType,
        city_name=graphene.String(required=True),
        days=graphene.Int(),
    )

    def resolve_current_weather(self, info, city_name: str) -> Optional[CurrentWeather]:
        try:
            city = City.objects.get(name=city_name)
            return CurrentWeather.objects.filter(city=city).first()
        except City.DoesNotExist:
            return None

    def resolve_forecasts(self, info, city_name: str, days: Optional[int] = None):
        try:
            city = City.objects.get(name=city_name)
            queryset = WeatherForecast.objects.filter(city=city).order_by('forecast_date')
            if days is not None:
                max_date = date.today() + timedelta(days=days)
                queryset = queryset.filter(forecast_date__lte=max_date)
            return queryset
        except City.DoesNotExist:
            return []


schema = graphene.Schema(query=Query)
