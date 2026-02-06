from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from weather_service.models import City, WeatherForecast, WeatherRecord
from weather_service.serializers import (
    CitySerializer,
    WeatherForecastSerializer,
    WeatherRecordSerializer,
)


class CityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for City model.
    Provides CRUD operations for cities.
    """

    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = "uuid"
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


class WeatherRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for WeatherRecord model.
    Provides CRUD operations for weather records.
    """

    queryset = WeatherRecord.objects.all()
    serializer_class = WeatherRecordSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["city__name"]


class WeatherForecastViewSet(viewsets.ModelViewSet):
    """
    ViewSet for WeatherForecast model.
    Provides CRUD operations for weather forecasts.
    """

    queryset = WeatherForecast.objects.all()
    serializer_class = WeatherForecastSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["city__name"]
