from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Weather
from .serializers import WeatherSerializer
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
        """Filter weather data by city if city_uuid is provided."""
        queryset = Weather.objects.all()
        city_uuid = self.request.query_params.get('city_uuid')
        if city_uuid:
            queryset = queryset.filter(city__uuid=city_uuid)
        return queryset

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
