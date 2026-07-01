from datetime import date, datetime, time, timezone

from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import NotFound, ValidationError

from weather.models import City
from weather.serializers import CitySerializer, WeatherRecordSerializer


class CityListView(generics.ListAPIView):
    serializer_class = CitySerializer

    def get_queryset(self):
        queryset = City.objects.order_by("name")
        search_name = self.request.query_params.get("search_name")
        if search_name:
            queryset = queryset.filter(name__icontains=search_name)
        return queryset


class CityDetailView(generics.RetrieveAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    lookup_field = "uuid"


class CityWeatherView(generics.RetrieveAPIView):
    """Current weather of a city: its most recent weather record."""

    queryset = City.objects.all()
    serializer_class = WeatherRecordSerializer
    lookup_field = "uuid"

    def get_object(self):
        city = super().get_object()
        record = city.weather_records.order_by("-observed_at").first()
        if record is None:
            raise NotFound(f"No weather record exists for city {city.name}.")
        return record


class CityWeatherHistoryView(generics.ListAPIView):
    """Historical weather records of a city within a start/end date range."""

    serializer_class = WeatherRecordSerializer

    def get_queryset(self):
        city = get_object_or_404(City, uuid=self.kwargs["uuid"])
        start = self._date_param("start")
        end = self._date_param("end")
        if start and end and start > end:
            raise ValidationError(
                {"detail": "start date must not be after end date."}
            )
        queryset = city.weather_records.order_by("observed_at")
        if start:
            queryset = queryset.filter(
                observed_at__gte=datetime.combine(start, time.min, tzinfo=timezone.utc)
            )
        if end:
            queryset = queryset.filter(
                observed_at__lte=datetime.combine(end, time.max, tzinfo=timezone.utc)
            )
        return queryset

    def _date_param(self, name):
        value = self.request.query_params.get(name)
        if value is None:
            return None
        try:
            return date.fromisoformat(value)
        except ValueError:
            raise ValidationError({name: "must be an ISO date (YYYY-MM-DD)."})
