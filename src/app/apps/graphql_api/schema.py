"""
GraphQL Schema for Weather Forecast Service.
"""
import graphene
from graphene_django import DjangoObjectType
from datetime import datetime

from apps.cities.models import City
from apps.weather.models import CurrentWeather
from apps.forecast.models import WeatherForecast
from apps.historical.models import WeatherHistory


class CityType(DjangoObjectType):
    """GraphQL type for City model."""

    class Meta:
        model = City
        fields = ('uuid', 'name', 'country', 'region', 'timezone', 'latitude', 'longitude')


class CurrentWeatherType(DjangoObjectType):
    """GraphQL type for CurrentWeather model."""

    class Meta:
        model = CurrentWeather
        fields = ('uuid', 'temperature', 'humidity', 'wind_speed', 'pressure',
                  'condition_code', 'condition', 'timestamp')


class WeatherForecastType(DjangoObjectType):
    """GraphQL type for WeatherForecast model."""

    class Meta:
        model = WeatherForecast
        fields = ('uuid', 'forecast_date', 'temperature', 'humidity', 'wind_speed', 'condition')


class WeatherHistoryType(DjangoObjectType):
    """GraphQL type for WeatherHistory model."""

    class Meta:
        model = WeatherHistory
        fields = ('uuid', 'date', 'temperature', 'humidity', 'wind_speed', 'condition')


class Query(graphene.ObjectType):
    """Root Query for GraphQL API."""

    # City queries
    all_cities = graphene.List(CityType)
    city = graphene.Field(CityType, uuid=graphene.UUID(required=True))

    # Current weather query
    current_weather = graphene.Field(CurrentWeatherType, city_uuid=graphene.UUID(required=True))

    # Forecast query
    forecast = graphene.List(WeatherForecastType, city_uuid=graphene.UUID(required=True))

    # Historical query
    historical_weather = graphene.Field(
        WeatherHistoryType,
        city_uuid=graphene.UUID(required=True),
        date=graphene.Date(required=True)
    )

    def resolve_all_cities(self, info):
        """Resolve all cities."""
        return City.objects.all()

    def resolve_city(self, info, uuid):
        """Resolve a single city by UUID."""
        try:
            return City.objects.get(uuid=uuid)
        except City.DoesNotExist:
            return None

    def resolve_current_weather(self, info, city_uuid):
        """Resolve current weather for a city."""
        try:
            city = City.objects.get(uuid=city_uuid)
            return CurrentWeather.objects.filter(city=city).first()
        except City.DoesNotExist:
            return None

    def resolve_forecast(self, info, city_uuid):
        """Resolve weather forecast for a city (up to 7 days)."""
        try:
            city = City.objects.get(uuid=city_uuid)
            return WeatherForecast.objects.filter(city=city)[:7]
        except City.DoesNotExist:
            return []

    def resolve_historical_weather(self, info, city_uuid, date):
        """Resolve historical weather for a city on a specific date."""
        try:
            city = City.objects.get(uuid=city_uuid)
            return WeatherHistory.objects.get(city=city, date=date)
        except (City.DoesNotExist, WeatherHistory.DoesNotExist):
            return None


schema = graphene.Schema(query=Query)
