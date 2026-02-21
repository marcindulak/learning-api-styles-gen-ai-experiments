"""
GraphQL schema for Weather Forecast Service using strawberry-django.
"""
from datetime import date
from typing import Optional
import strawberry
import strawberry_django
from strawberry.types import Info
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from .models import City, WeatherRecord, Forecast


@strawberry_django.type(City)
class CityType:
    """GraphQL type for City model."""
    uuid: strawberry.auto
    name: strawberry.auto
    country: strawberry.auto
    region: strawberry.auto
    timezone: strawberry.auto
    latitude: strawberry.auto
    longitude: strawberry.auto
    created_at: strawberry.auto
    updated_at: strawberry.auto


@strawberry_django.type(WeatherRecord)
class WeatherRecordType:
    """GraphQL type for WeatherRecord model."""
    uuid: strawberry.auto
    city: CityType
    recorded_at: strawberry.auto
    temperature: strawberry.auto
    feels_like: strawberry.auto
    humidity: strawberry.auto
    wind_speed: strawberry.auto
    wind_direction: strawberry.auto
    pressure: strawberry.auto
    precipitation: strawberry.auto
    uv_index: strawberry.auto
    visibility: strawberry.auto
    cloud_cover: strawberry.auto
    description: strawberry.auto


@strawberry_django.type(Forecast)
class ForecastType:
    """GraphQL type for Forecast model."""
    uuid: strawberry.auto
    city: CityType
    forecast_date: strawberry.auto
    temperature_high: strawberry.auto
    temperature_low: strawberry.auto
    humidity: strawberry.auto
    wind_speed: strawberry.auto
    precipitation_probability: strawberry.auto
    description: strawberry.auto
    created_at: strawberry.auto


@strawberry_django.input(City)
class CityInput:
    """Input type for creating/updating cities."""
    name: strawberry.auto
    country: strawberry.auto
    region: strawberry.auto
    timezone: strawberry.auto
    latitude: strawberry.auto
    longitude: strawberry.auto


@strawberry_django.input(WeatherRecord)
class WeatherRecordInput:
    """Input type for creating weather records."""
    city: strawberry.auto
    recorded_at: strawberry.auto
    temperature: strawberry.auto
    feels_like: strawberry.auto
    humidity: strawberry.auto
    wind_speed: strawberry.auto
    wind_direction: strawberry.auto
    pressure: strawberry.auto
    precipitation: strawberry.auto
    uv_index: strawberry.auto
    visibility: strawberry.auto
    cloud_cover: strawberry.auto
    description: strawberry.auto


@strawberry_django.input(Forecast)
class ForecastInput:
    """Input type for creating forecasts."""
    city: strawberry.auto
    forecast_date: strawberry.auto
    temperature_high: strawberry.auto
    temperature_low: strawberry.auto
    humidity: strawberry.auto
    wind_speed: strawberry.auto
    precipitation_probability: strawberry.auto
    description: strawberry.auto


@strawberry.type
class Query:
    """GraphQL queries."""

    @strawberry_django.field
    def cities(self, info: Info, name: Optional[str] = None) -> list[CityType]:
        """Query all cities with optional name filter."""
        queryset = City.objects.all()
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset

    @strawberry_django.field
    def city(self, info: Info, uuid: strawberry.ID) -> Optional[CityType]:
        """Query a single city by UUID."""
        try:
            return City.objects.get(uuid=uuid)
        except City.DoesNotExist:
            return None

    @strawberry_django.field
    def weather_records(
        self,
        info: Info,
        city_uuid: Optional[strawberry.ID] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> list[WeatherRecordType]:
        """Query weather records with optional filters."""
        queryset = WeatherRecord.objects.select_related('city').order_by('-recorded_at')

        if city_uuid:
            queryset = queryset.filter(city__uuid=city_uuid)

        if date_from:
            queryset = queryset.filter(recorded_at__gte=date_from)

        if date_to:
            queryset = queryset.filter(recorded_at__lte=date_to)

        return queryset

    @strawberry_django.field
    def forecasts(
        self,
        info: Info,
        city_uuid: Optional[strawberry.ID] = None,
    ) -> list[ForecastType]:
        """Query forecasts with optional city filter."""
        queryset = Forecast.objects.select_related('city').order_by('forecast_date')

        if city_uuid:
            queryset = queryset.filter(city__uuid=city_uuid)

        return queryset


@strawberry.type
class Mutation:
    """GraphQL mutations (admin only)."""

    @strawberry_django.mutation
    def create_city(self, info: Info, input: CityInput) -> CityType:
        """Create a new city (admin only)."""
        if not info.context.request.user.is_authenticated:
            raise PermissionError("Authentication required")

        if not info.context.request.user.is_staff:
            raise PermissionError("Admin access required")

        try:
            data = vars(input)
            city = City.objects.create(**data)
            return city
        except IntegrityError:
            raise ValueError("A city with this name and country already exists")

    @strawberry_django.mutation
    def update_city(self, info: Info, uuid: strawberry.ID, input: CityInput) -> CityType:
        """Update an existing city (admin only)."""
        if not info.context.request.user.is_authenticated:
            raise PermissionError("Authentication required")

        if not info.context.request.user.is_staff:
            raise PermissionError("Admin access required")

        try:
            city = City.objects.get(uuid=uuid)
            for field, value in vars(input).items():
                setattr(city, field, value)
            city.save()
            return city
        except City.DoesNotExist:
            raise ValueError(f"City with UUID {uuid} not found")
        except IntegrityError as e:
            raise ValueError(f"Update failed: {str(e)}")

    @strawberry_django.mutation
    def delete_city(self, info: Info, uuid: strawberry.ID) -> bool:
        """Delete a city (admin only)."""
        if not info.context.request.user.is_authenticated:
            raise PermissionError("Authentication required")

        if not info.context.request.user.is_staff:
            raise PermissionError("Admin access required")

        try:
            city = City.objects.get(uuid=uuid)
            city.delete()
            return True
        except City.DoesNotExist:
            raise ValueError(f"City with UUID {uuid} not found")

    @strawberry_django.mutation
    def create_weather_record(self, info: Info, input: WeatherRecordInput) -> WeatherRecordType:
        """Create a new weather record (admin only)."""
        if not info.context.request.user.is_authenticated:
            raise PermissionError("Authentication required")

        if not info.context.request.user.is_staff:
            raise PermissionError("Admin access required")

        try:
            data = vars(input)
            # Convert city UUID to City instance
            city_id = data.pop('city')
            city = City.objects.get(uuid=city_id)
            record = WeatherRecord.objects.create(city=city, **data)
            return record
        except City.DoesNotExist:
            raise ValueError(f"City not found")
        except IntegrityError as e:
            raise ValueError(f"Failed to create weather record: {str(e)}")

    @strawberry_django.mutation
    def create_forecast(self, info: Info, input: ForecastInput) -> ForecastType:
        """Create a new forecast (admin only)."""
        if not info.context.request.user.is_authenticated:
            raise PermissionError("Authentication required")

        if not info.context.request.user.is_staff:
            raise PermissionError("Admin access required")

        try:
            data = vars(input)
            # Convert city UUID to City instance
            city_id = data.pop('city')
            city = City.objects.get(uuid=city_id)
            forecast = Forecast(city=city, **data)
            # This will trigger full_clean() which validates the 7-day limit
            forecast.save()
            return forecast
        except City.DoesNotExist:
            raise ValueError("City not found")
        except IntegrityError:
            raise ValueError("A forecast for this city and date already exists")
        except ValidationError as e:
            # Catch validation errors from model.full_clean()
            raise ValueError(str(e))


schema = strawberry.Schema(query=Query, mutation=Mutation)
