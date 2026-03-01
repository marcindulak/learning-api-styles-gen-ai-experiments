"""GraphQL schema for weather data."""
import graphene
from graphene_django import DjangoObjectType

from .models import City, WeatherAlert, WeatherForecast, WeatherRecord


class CityType(DjangoObjectType):
    """City GraphQL type."""

    class Meta:
        model = City
        fields = '__all__'


class WeatherRecordType(DjangoObjectType):
    """Weather record GraphQL type."""

    class Meta:
        model = WeatherRecord
        fields = '__all__'


class WeatherForecastType(DjangoObjectType):
    """Weather forecast GraphQL type."""

    class Meta:
        model = WeatherForecast
        fields = '__all__'


class WeatherAlertType(DjangoObjectType):
    """Weather alert GraphQL type."""

    class Meta:
        model = WeatherAlert
        fields = '__all__'


class Query(graphene.ObjectType):
    """GraphQL queries."""

    cities = graphene.List(CityType, name=graphene.String())
    city = graphene.Field(CityType, uuid=graphene.UUID(required=True))

    weather_records = graphene.List(WeatherRecordType, city_uuid=graphene.UUID())
    weather_record = graphene.Field(WeatherRecordType, uuid=graphene.UUID(required=True))

    weather_forecasts = graphene.List(WeatherForecastType, city_uuid=graphene.UUID())
    weather_forecast = graphene.Field(WeatherForecastType, uuid=graphene.UUID(required=True))

    weather_alerts = graphene.List(WeatherAlertType, city_uuid=graphene.UUID(), is_active=graphene.Boolean())
    weather_alert = graphene.Field(WeatherAlertType, uuid=graphene.UUID(required=True))

    def resolve_cities(self, info, name: str | None = None):
        """Resolve cities query."""
        queryset = City.objects.all()
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset

    def resolve_city(self, info, uuid: str):
        """Resolve city query."""
        return City.objects.get(uuid=uuid)

    def resolve_weather_records(self, info, city_uuid: str | None = None):
        """Resolve weather records query."""
        queryset = WeatherRecord.objects.select_related('city').all()
        if city_uuid:
            queryset = queryset.filter(city__uuid=city_uuid)
        return queryset

    def resolve_weather_record(self, info, uuid: str):
        """Resolve weather record query."""
        return WeatherRecord.objects.get(uuid=uuid)

    def resolve_weather_forecasts(self, info, city_uuid: str | None = None):
        """Resolve weather forecasts query."""
        queryset = WeatherForecast.objects.select_related('city').all()
        if city_uuid:
            queryset = queryset.filter(city__uuid=city_uuid)
        return queryset

    def resolve_weather_forecast(self, info, uuid: str):
        """Resolve weather forecast query."""
        return WeatherForecast.objects.get(uuid=uuid)

    def resolve_weather_alerts(self, info, city_uuid: str | None = None, is_active: bool | None = None):
        """Resolve weather alerts query."""
        queryset = WeatherAlert.objects.select_related('city').all()
        if city_uuid:
            queryset = queryset.filter(city__uuid=city_uuid)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        return queryset

    def resolve_weather_alert(self, info, uuid: str):
        """Resolve weather alert query."""
        return WeatherAlert.objects.get(uuid=uuid)


schema = graphene.Schema(query=Query)
