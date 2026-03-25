from typing import List, Optional
import strawberry
from strawberry import django as strawberry_django
from .models import City, WeatherRecord, WeatherForecast


@strawberry_django.type(City)
class CityType:
    uuid: strawberry.ID
    name: str
    country: str
    region: str
    timezone: str
    latitude: float
    longitude: float


@strawberry_django.type(WeatherRecord)
class WeatherRecordType:
    uuid: strawberry.ID
    recorded_at: str
    temperature_celsius: float
    humidity_percent: float
    wind_speed_kmh: float
    precipitation_mm: float
    description: str


@strawberry_django.type(WeatherForecast)
class WeatherForecastType:
    uuid: strawberry.ID
    forecast_date: str
    temperature_max_celsius: float
    temperature_min_celsius: float
    precipitation_mm: float
    wind_speed_kmh: float
    description: str


@strawberry.type
class Query:
    @strawberry.field
    def cities(self) -> List[CityType]:
        return list(City.objects.all())

    @strawberry.field
    def city(self, uuid: strawberry.ID) -> Optional[CityType]:
        try:
            return City.objects.get(uuid=uuid)
        except City.DoesNotExist:
            return None

    @strawberry.field
    def weather_records(self, city_uuid: strawberry.ID) -> List[WeatherRecordType]:
        return list(WeatherRecord.objects.filter(city__uuid=city_uuid))

    @strawberry.field
    def forecasts(self, city_uuid: strawberry.ID) -> List[WeatherForecastType]:
        return list(WeatherForecast.objects.filter(city__uuid=city_uuid))


schema = strawberry.Schema(query=Query)
