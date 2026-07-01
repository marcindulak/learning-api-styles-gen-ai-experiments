from rest_framework import generics
from rest_framework.exceptions import NotFound

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
