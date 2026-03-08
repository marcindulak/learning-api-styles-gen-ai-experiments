"""
Views for weather API endpoints.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
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
    """
    queryset = CurrentWeather.objects.all()
    serializer_class = CurrentWeatherSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """
        Filter current weather by city name if city_name query parameter is provided.
        """
        queryset = CurrentWeather.objects.all()
        city_name = self.request.query_params.get('city_name', None)
        if city_name is not None:
            queryset = queryset.filter(city__name=city_name)
        return queryset


class WeatherForecastViewSet(viewsets.ModelViewSet):
    """
    ViewSet for WeatherForecast model.
    Admin users can create/update/delete weather forecasts.
    """
    queryset = WeatherForecast.objects.all()
    serializer_class = WeatherForecastSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """
        Filter weather forecasts by city name if city_name query parameter is provided.
        """
        queryset = WeatherForecast.objects.all()
        city_name = self.request.query_params.get('city_name', None)
        if city_name is not None:
            queryset = queryset.filter(city__name=city_name)
        return queryset
