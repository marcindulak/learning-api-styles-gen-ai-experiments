"""GraphQL schema using Strawberry."""

import uuid as _uuid
from datetime import datetime
from typing import Optional

import strawberry
import strawberry_django
from strawberry.types import Info

from .models import City as CityModel
from .models import WeatherAlert as AlertModel
from .models import WeatherForecast as ForecastModel
from .models import WeatherRecord as RecordModel


@strawberry_django.type(CityModel)
class CityType:
    uuid: _uuid.UUID
    name: str
    country: str
    region: str
    timezone: str
    latitude: float
    longitude: float


@strawberry_django.type(RecordModel)
class WeatherRecordType:
    uuid: _uuid.UUID
    timestamp: datetime
    temperature: float
    feels_like: float
    humidity: int
    pressure: float
    wind_speed: float
    wind_direction: int
    precipitation: float
    visibility: int
    uv_index: float
    cloud_cover: int
    description: str


@strawberry_django.type(ForecastModel)
class ForecastType:
    uuid: _uuid.UUID
    forecast_date: strawberry.auto
    temperature_high: float
    temperature_low: float
    humidity: int
    precipitation_prob: int
    wind_speed: float
    description: str


@strawberry_django.type(AlertModel)
class AlertType:
    uuid: _uuid.UUID
    severity: str
    event: str
    description: str
    starts_at: datetime
    expires_at: datetime
    active: bool


def _check_admin(info: Info):
    user = info.context.request.user
    if not user.is_authenticated:
        raise PermissionError("Authentication required")
    if not user.is_staff:
        raise PermissionError("Permission denied")


@strawberry.input
class CityInput:
    name: str
    country: str
    region: str
    timezone: str
    latitude: float
    longitude: float


@strawberry.input
class WeatherRecordInput:
    timestamp: datetime
    temperature: float
    feels_like: float
    humidity: int
    pressure: float
    wind_speed: float
    wind_direction: int
    precipitation: float
    visibility: int
    uv_index: float
    cloud_cover: int
    description: str


@strawberry.input
class ForecastInput:
    forecast_date: strawberry.auto
    temperature_high: float
    temperature_low: float
    humidity: int
    precipitation_prob: int
    wind_speed: float
    description: str


@strawberry.input
class AlertInput:
    city_uuid: _uuid.UUID
    severity: str
    event: str
    description: str
    starts_at: datetime
    expires_at: datetime


@strawberry.type
class Query:
    @strawberry.field
    def cities(self) -> list[CityType]:
        return CityModel.objects.all()

    @strawberry.field
    def city(self, uuid: _uuid.UUID) -> Optional[CityType]:
        try:
            return CityModel.objects.get(uuid=uuid)
        except CityModel.DoesNotExist:
            return None

    @strawberry.field
    def weather_records(
        self,
        city_uuid: _uuid.UUID,
        from_: Optional[datetime] = None,
        to: Optional[datetime] = None,
    ) -> list[WeatherRecordType]:
        qs = RecordModel.objects.filter(city__uuid=city_uuid)
        if from_:
            qs = qs.filter(timestamp__gte=from_)
        if to:
            qs = qs.filter(timestamp__lte=to)
        return qs

    @strawberry.field
    def forecasts(self, city_uuid: _uuid.UUID) -> list[ForecastType]:
        return ForecastModel.objects.filter(city__uuid=city_uuid)

    @strawberry.field
    def alerts(
        self,
        city_uuid: Optional[_uuid.UUID] = None,
        active: Optional[bool] = None,
    ) -> list[AlertType]:
        qs = AlertModel.objects.all()
        if city_uuid:
            qs = qs.filter(city__uuid=city_uuid)
        if active is not None:
            qs = qs.filter(active=active)
        return qs


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_city(self, input: CityInput, info: Info) -> CityType:
        _check_admin(info)
        return CityModel.objects.create(**strawberry.asdict(input))

    @strawberry.mutation
    def update_city(self, uuid: _uuid.UUID, input: CityInput, info: Info) -> CityType:
        _check_admin(info)
        city = CityModel.objects.get(uuid=uuid)
        for key, value in strawberry.asdict(input).items():
            setattr(city, key, value)
        city.save()
        return city

    @strawberry.mutation
    def delete_city(self, uuid: _uuid.UUID, info: Info) -> bool:
        _check_admin(info)
        city = CityModel.objects.get(uuid=uuid)
        city.delete()
        return True

    @strawberry.mutation
    def create_weather_record(
        self, city_uuid: _uuid.UUID, input: WeatherRecordInput, info: Info
    ) -> WeatherRecordType:
        _check_admin(info)
        city = CityModel.objects.get(uuid=city_uuid)
        return RecordModel.objects.create(city=city, **strawberry.asdict(input))

    @strawberry.mutation
    def create_forecast(
        self, city_uuid: _uuid.UUID, input: ForecastInput, info: Info
    ) -> ForecastType:
        _check_admin(info)
        city = CityModel.objects.get(uuid=city_uuid)
        return ForecastModel.objects.create(city=city, **strawberry.asdict(input))

    @strawberry.mutation
    def create_alert(self, input: AlertInput, info: Info) -> AlertType:
        _check_admin(info)
        data = strawberry.asdict(input)
        city_uuid = data.pop("city_uuid")
        city = CityModel.objects.get(uuid=city_uuid)
        return AlertModel.objects.create(city=city, **data)


schema = strawberry.Schema(query=Query, mutation=Mutation)
