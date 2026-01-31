from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.cities.models import City
from .models import CurrentWeather
from .serializers import CurrentWeatherSerializer, CurrentWeatherCreateSerializer


class CityWeatherView(APIView):
    """
    View for getting or creating current weather data for a city.
    GET: Returns the latest current weather for a city.
    POST: Creates new current weather data (for admin/testing purposes).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, uuid):
        """Get current weather for a city by its UUID."""
        try:
            city = City.objects.get(uuid=uuid)
        except City.DoesNotExist:
            return Response(
                {'error': 'City not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get the most recent weather data for this city
        weather = CurrentWeather.objects.filter(city=city).first()

        if weather is None:
            return Response(
                {'error': 'No current weather data available for this city'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CurrentWeatherSerializer(weather)
        return Response(serializer.data)

    def post(self, request, uuid):
        """Create current weather data for a city."""
        try:
            city = City.objects.get(uuid=uuid)
        except City.DoesNotExist:
            return Response(
                {'error': 'City not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Add the city UUID to the request data
        data = request.data.copy()
        data['city_uuid'] = str(uuid)

        serializer = CurrentWeatherCreateSerializer(data=data)
        if serializer.is_valid():
            weather = serializer.save()
            return Response(
                CurrentWeatherSerializer(weather).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WeatherByUUIDView(APIView):
    """
    View for getting current weather by non-existent city UUID.
    This is mainly to return 404 for non-existent cities.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, uuid):
        """Get current weather for a city by its UUID."""
        try:
            city = City.objects.get(uuid=uuid)
        except City.DoesNotExist:
            return Response(
                {'error': 'City not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        weather = CurrentWeather.objects.filter(city=city).first()

        if weather is None:
            return Response(
                {'error': 'No current weather data available for this city'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CurrentWeatherSerializer(weather)
        return Response(serializer.data)
