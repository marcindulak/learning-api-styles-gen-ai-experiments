import graphene
from graphene_django import DjangoObjectType

from weather_service.models import City, WeatherRecord


class CityType(DjangoObjectType):
    class Meta:
        model = City
        fields = ("uuid", "name", "country", "region", "timezone", "latitude", "longitude")


class WeatherRecordType(DjangoObjectType):
    class Meta:
        model = WeatherRecord
        fields = ("id", "city", "timestamp", "temperature", "humidity", "pressure", "wind_speed", "precipitation")


class Query(graphene.ObjectType):
    cities = graphene.List(CityType)
    city = graphene.Field(CityType, name=graphene.String(required=True))
    weather_data = graphene.List(WeatherRecordType, city=graphene.String(required=True))

    def resolve_cities(self, info):
        return City.objects.all()

    def resolve_city(self, info, name):
        return City.objects.filter(name=name).first()

    def resolve_weather_data(self, info, city):
        return WeatherRecord.objects.filter(city__name=city)


schema = graphene.Schema(query=Query)
