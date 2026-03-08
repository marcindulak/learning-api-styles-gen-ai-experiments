"""
Views for weather API endpoints.
"""
import os
from datetime import datetime
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.urls import reverse
from weather.models import City, CurrentWeather, WeatherForecast, WeatherAlert
from weather.serializers import CitySerializer, CurrentWeatherSerializer, WeatherForecastSerializer, WeatherAlertSerializer
from weather.weather_api_service import WeatherAPIService


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


@api_view(['POST'])
@permission_classes([IsAdminUser])
def fetch_weather_from_api(request):
    """
    Admin endpoint to fetch weather data from third-party API.
    Expected POST data: {"city_name": "London", "data_type": "current"} or {"city_name": "Paris", "data_type": "forecast"}
    """
    city_name = request.data.get('city_name')
    data_type = request.data.get('data_type', 'current')

    if not city_name:
        return Response(
            {'error': 'city_name is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        city = City.objects.get(name=city_name)
    except City.DoesNotExist:
        return Response(
            {'error': f'City {city_name} not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    weather_service = WeatherAPIService()

    if data_type == 'current':
        weather_data = weather_service.fetch_current_weather(
            city.name,
            city.latitude,
            city.longitude
        )

        if weather_data is None:
            return Response(
                {'error': 'Third-party weather API is unavailable'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        CurrentWeather.objects.create(
            city=city,
            temperature=weather_data['temperature'],
            humidity=weather_data['humidity'],
            pressure=weather_data['pressure'],
            wind_speed=weather_data['wind_speed']
        )

        return Response({
            'message': f'Current weather data fetched and stored for {city_name}'
        }, status=status.HTTP_200_OK)

    elif data_type == 'forecast':
        forecast_data = weather_service.fetch_forecast(
            city.name,
            city.latitude,
            city.longitude,
            days=7
        )

        if forecast_data is None:
            return Response(
                {'error': 'Third-party weather API is unavailable'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        for forecast in forecast_data:
            WeatherForecast.objects.update_or_create(
                city=city,
                forecast_date=forecast['forecast_date'],
                defaults={
                    'temperature': forecast['temperature'],
                    'humidity': forecast['humidity'],
                    'pressure': forecast['pressure'],
                    'wind_speed': forecast['wind_speed']
                }
            )

        return Response({
            'message': f'Forecast data fetched and stored for {city_name}'
        }, status=status.HTTP_200_OK)

    else:
        return Response(
            {'error': 'Invalid data_type. Must be "current" or "forecast"'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([])
def set_test_mode(request):
    """
    Test endpoint to set weather API test mode.
    Expected POST data: {"mode": "available"} or {"mode": "unavailable"}
    """
    mode = request.data.get('mode', 'available')
    os.environ['WEATHER_API_TEST_MODE'] = mode
    return Response({'message': f'Test mode set to {mode}'}, status=status.HTTP_200_OK)


class ForecastAtomFeed(Feed):
    """
    Atom feed for weather forecasts.
    """
    feed_type = Atom1Feed

    def get_object(self, request, city_name):
        """
        Get the city object from the URL parameter.
        """
        return get_object_or_404(City, name=city_name)

    def title(self, obj):
        """
        Feed title.
        """
        return f"Weather Forecast for {obj.name}"

    def link(self, obj):
        """
        Feed link.
        """
        return f"/feeds/forecast/{obj.name}/"

    def description(self, obj):
        """
        Feed description.
        """
        return f"Weather forecast feed for {obj.name}"

    def items(self, obj):
        """
        Return forecast items for the city.
        """
        return WeatherForecast.objects.filter(city=obj).order_by('forecast_date')

    def item_title(self, item):
        """
        Title for each forecast entry.
        """
        return f"Forecast for {item.city.name} on {item.forecast_date}"

    def item_description(self, item):
        """
        Description for each forecast entry.
        """
        return (
            f"Temperature: {item.temperature}°C, "
            f"Humidity: {item.humidity}%, "
            f"Pressure: {item.pressure} hPa, "
            f"Wind Speed: {item.wind_speed} m/s"
        )

    def item_link(self, item):
        """
        Link for each forecast entry.
        """
        return f"/feeds/forecast/{item.city.name}/"

    def item_pubdate(self, item):
        """
        Publication date for each forecast entry.
        """
        return datetime.combine(item.forecast_date, datetime.min.time())


class WeatherAlertViewSet(viewsets.ModelViewSet):
    """
    ViewSet for WeatherAlert model.
    Admin users can create weather alerts.
    Alerts are automatically broadcast to subscribed WebSocket clients.
    """
    queryset = WeatherAlert.objects.all()
    serializer_class = WeatherAlertSerializer
    permission_classes = [IsAdminUser]
