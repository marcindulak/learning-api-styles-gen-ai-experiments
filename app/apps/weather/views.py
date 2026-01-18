from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Weather, Forecast
from .serializers import WeatherSerializer, ForecastSerializer
from apps.cities.models import City


class WeatherViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Weather data.
    Provides read-only operations to retrieve weather data for cities.
    """
    queryset = Weather.objects.all()
    serializer_class = WeatherSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'

    def get_queryset(self):
        """Filter weather data by city if city_uuid or city name is provided."""
        queryset = Weather.objects.all()
        city_uuid = self.request.query_params.get('city_uuid')
        city_name = self.request.query_params.get('city')

        if city_uuid:
            queryset = queryset.filter(city__uuid=city_uuid)
        elif city_name:
            queryset = queryset.filter(city__name=city_name)

        return queryset

    def list(self, request, *args, **kwargs):
        """
        List weather data. If city parameter is provided and city doesn't exist, return 404.
        """
        city_name = request.query_params.get('city')

        # If city parameter is provided, verify the city exists
        if city_name:
            city = get_object_or_404(City, name=city_name)

        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def current(self, request):
        """
        Get the most recent weather data for a specific city.
        Query parameter: city_uuid (required)
        """
        city_uuid = request.query_params.get('city_uuid')
        if not city_uuid:
            return Response({'error': 'city_uuid parameter is required'}, status=400)

        city = get_object_or_404(City, uuid=city_uuid)
        weather = Weather.objects.filter(city=city).first()

        if not weather:
            return Response({'error': 'No weather data found for this city'}, status=404)

        serializer = self.get_serializer(weather)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_city(self, request):
        """
        Get weather data for a specific city by name.
        Query parameter: city_name (required)
        """
        city_name = request.query_params.get('city_name')
        if not city_name:
            return Response({'error': 'city_name parameter is required'}, status=400)

        city = get_object_or_404(City, name=city_name)
        weather = Weather.objects.filter(city=city).first()

        if not weather:
            return Response({'error': 'No weather data found for this city'}, status=404)

        serializer = self.get_serializer(weather)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def forecast(self, request):
        """
        Get weather forecast data for a specific city.
        Query parameter: city_uuid (required)
        Returns up to 7 days of forecast data in chronological order.
        """
        city_uuid = request.query_params.get('city_uuid')
        if not city_uuid:
            return Response({'error': 'city_uuid parameter is required'}, status=400)

        city = get_object_or_404(City, uuid=city_uuid)
        forecasts = Forecast.objects.filter(city=city).order_by('forecast_date')[:7]

        if not forecasts:
            return Response({'error': 'No forecast data found for this city'}, status=404)

        serializer = ForecastSerializer(forecasts, many=True)
        return Response(serializer.data)
