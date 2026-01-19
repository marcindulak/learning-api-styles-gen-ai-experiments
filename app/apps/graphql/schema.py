"""
GraphQL Schema for Weather Forecast Service
"""
import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth.models import User
from apps.cities.models import City
from apps.weather.models import Weather


class CityType(DjangoObjectType):
    """GraphQL type for City model"""
    class Meta:
        model = City
        fields = ('uuid', 'name', 'country', 'region', 'timezone', 'latitude', 'longitude')


class WeatherType(DjangoObjectType):
    """GraphQL type for Weather model"""
    wind_speed = graphene.Float()

    class Meta:
        model = Weather
        fields = ('uuid', 'city', 'temperature', 'humidity', 'wind_speed', 'pressure', 'description', 'timestamp')

    def resolve_wind_speed(self, info):
        return self.wind_speed


class Query(graphene.ObjectType):
    """Root query type"""
    weather_by_city = graphene.Field(WeatherType, city_name=graphene.String(required=True))
    weather_list = graphene.List(WeatherType)
    city = graphene.Field(CityType, uuid=graphene.String(required=True))
    cities = graphene.List(CityType)

    def resolve_weather_by_city(self, info, city_name):
        """
        Resolve weather data for a specific city by name.
        Returns the most recent weather data for the city.
        """
        try:
            city = City.objects.get(name=city_name)
            weather = Weather.objects.filter(city=city).first()
            return weather
        except City.DoesNotExist:
            return None

    def resolve_weather_list(self, info):
        """Resolve list of all weather records"""
        return Weather.objects.all()

    def resolve_city(self, info, uuid):
        """Resolve a specific city by UUID"""
        try:
            return City.objects.get(uuid=uuid)
        except City.DoesNotExist:
            return None

    def resolve_cities(self, info):
        """Resolve list of all cities"""
        return City.objects.all()


schema = graphene.Schema(query=Query)
