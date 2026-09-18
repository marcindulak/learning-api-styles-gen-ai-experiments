import strawberry

from .models import WeatherRecord


@strawberry.type
class CurrentWeatherType:
    temperature: float
    humidity: int
    wind_speed: float
    precipitation_probability: int
    condition: str


@strawberry.type
class Query:
    @strawberry.field
    def current_weather(self, city_uuid: str) -> CurrentWeatherType | None:
        return WeatherRecord.objects.filter(city__uuid=city_uuid).latest()


schema = strawberry.Schema(query=Query)
