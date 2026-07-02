"""GraphQL schema of the Weather Forecast Service.

Field names are snake_case in Python and exposed as camelCase by
graphene (wind_speed -> windSpeed).
"""
import graphene

from weather.models import WeatherRecord


class WeatherType(graphene.ObjectType):
    temperature = graphene.Float()
    humidity = graphene.Float()
    wind_speed = graphene.Float()
    pressure = graphene.Float()
    precipitation = graphene.Float()
    observed_at = graphene.DateTime()
    source = graphene.String()


class Query(graphene.ObjectType):
    weather = graphene.Field(
        WeatherType,
        city_name=graphene.String(required=True),
        description="Current weather (most recent record) of a city",
    )

    def resolve_weather(root, info, city_name):
        return (
            WeatherRecord.objects.filter(city__name=city_name)
            .order_by("-observed_at")
            .first()
        )


schema = graphene.Schema(query=Query)
