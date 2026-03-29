from typing import List, Optional
from datetime import datetime, date
import strawberry
from .models import City, WeatherRecord, WeatherForecast


@strawberry.type
class CityType:
    uuid: str
    name: str
    country: str
    region: str
    timezone: str
    latitude: float
    longitude: float


@strawberry.type
class WeatherRecordType:
    uuid: str
    recorded_at: datetime
    temperature_celsius: float
    humidity_percent: float
    wind_speed_kmh: float
    precipitation_mm: float
    description: str


@strawberry.type
class WeatherForecastType:
    uuid: str
    forecast_date: date
    temperature_max_celsius: float
    temperature_min_celsius: float
    precipitation_mm: float
    wind_speed_kmh: float
    description: str


@strawberry.type
class Query:
    @strawberry.field
    def cities(self) -> List[CityType]:
        return [
            CityType(
                uuid=str(c.uuid),
                name=c.name,
                country=c.country,
                region=c.region,
                timezone=c.timezone,
                latitude=c.latitude,
                longitude=c.longitude,
            )
            for c in City.objects.all()
        ]

    @strawberry.field
    def city(self, uuid: str) -> Optional[CityType]:
        try:
            c = City.objects.get(uuid=uuid)
            return CityType(
                uuid=str(c.uuid),
                name=c.name,
                country=c.country,
                region=c.region,
                timezone=c.timezone,
                latitude=c.latitude,
                longitude=c.longitude,
            )
        except City.DoesNotExist:
            return None

    @strawberry.field
    def weather_records(self, city_uuid: str) -> List[WeatherRecordType]:
        return [
            WeatherRecordType(
                uuid=str(r.uuid),
                recorded_at=r.recorded_at,
                temperature_celsius=r.temperature_celsius,
                humidity_percent=r.humidity_percent,
                wind_speed_kmh=r.wind_speed_kmh,
                precipitation_mm=r.precipitation_mm,
                description=r.description,
            )
            for r in WeatherRecord.objects.filter(city__uuid=city_uuid)
        ]

    @strawberry.field
    def forecasts(self, city_uuid: str) -> List[WeatherForecastType]:
        return [
            WeatherForecastType(
                uuid=str(f.uuid),
                forecast_date=f.forecast_date,
                temperature_max_celsius=f.temperature_max_celsius,
                temperature_min_celsius=f.temperature_min_celsius,
                precipitation_mm=f.precipitation_mm,
                wind_speed_kmh=f.wind_speed_kmh,
                description=f.description,
            )
            for f in WeatherForecast.objects.filter(city__uuid=city_uuid)
        ]


schema = strawberry.Schema(query=Query)
