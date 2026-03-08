"""
Views for weather API endpoints.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from weather.models import City, CurrentWeather, WeatherForecast
from weather.serializers import CitySerializer, CurrentWeatherSerializer, WeatherForecastSerializer


class CityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for City model.
    Admin users can create/update/delete cities.
    All users (including unauthenticated) can view cities.
    """
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        """
        Use IsAdminUser permission for write operations (create, update, delete).
        Use IsAuthenticatedOrReadOnly for read operations (list, retrieve).
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]

    def get_queryset(self):
        """
        Filter cities by name if search_name query parameter is provided.
        """
        queryset = City.objects.all()
        search_name = self.request.query_params.get('search_name', None)
        if search_name is not None:
            queryset = queryset.filter(name__icontains=search_name)
        return queryset


class CurrentWeatherViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CurrentWeather model.
    Admin users can create/update/delete current weather data.
    Unauthenticated users can retrieve current weather by city name.
    """
    queryset = CurrentWeather.objects.all()
    serializer_class = CurrentWeatherSerializer
    lookup_field = 'city__name'
    lookup_url_kwarg = 'city_name'
    permission_classes = []

    def get_permissions(self):
        """
        Use IsAdminUser permission for write operations.
        Allow unauthenticated access for retrieve operations.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'list']:
            return [IsAdminUser()]
        return []

    def get_queryset(self):
        """
        Filter current weather by city name if city_name query parameter is provided.
        """
        queryset = CurrentWeather.objects.all()
        city_name = self.request.query_params.get('city_name', None)
        if city_name is not None:
            queryset = queryset.filter(city__name=city_name)
        return queryset

    def retrieve(self, request, city_name=None):
        """
        Retrieve the most recent current weather for a city by name.
        """
        city = get_object_or_404(City, name=city_name)
        current_weather = CurrentWeather.objects.filter(city=city).order_by('-timestamp').first()

        if not current_weather:
            return Response(
                {'detail': f'No current weather data found for {city_name}'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(current_weather)
        return Response(serializer.data)


class WeatherForecastViewSet(viewsets.ModelViewSet):
    """
    ViewSet for WeatherForecast model.
    Admin users can create/update/delete weather forecasts.
    Unauthenticated users can retrieve forecasts by city name.
    """
    queryset = WeatherForecast.objects.all()
    serializer_class = WeatherForecastSerializer
    lookup_field = 'city__name'
    lookup_url_kwarg = 'city_name'
    permission_classes = []

    def get_permissions(self):
        """
        Use IsAdminUser permission for write operations.
        Allow unauthenticated access for retrieve operations.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'list']:
            return [IsAdminUser()]
        return []

    def get_queryset(self):
        """
        Filter weather forecasts by city name if city_name query parameter is provided.
        """
        queryset = WeatherForecast.objects.all()
        city_name = self.request.query_params.get('city_name', None)
        if city_name is not None:
            queryset = queryset.filter(city__name=city_name)
        return queryset

    def retrieve(self, request, city_name=None):
        """
        Retrieve all forecasts for a city by name, ordered by date.
        """
        city = get_object_or_404(City, name=city_name)
        forecasts = WeatherForecast.objects.filter(city=city).order_by('forecast_date')

        if not forecasts.exists():
            return Response(
                {'detail': f'No forecast data found for {city_name}'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(forecasts, many=True)
        return Response(serializer.data)
