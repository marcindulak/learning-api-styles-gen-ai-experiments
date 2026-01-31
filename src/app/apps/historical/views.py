from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.cities.models import City
from .models import WeatherHistory
from .serializers import WeatherHistorySerializer, WeatherHistoryCreateSerializer


class HistoricalViewSet(viewsets.ViewSet):
    """
    ViewSet for historical weather data retrieval and creation.
    """
    permission_classes = [IsAuthenticated]

    def list(self, request, city_uuid=None):
        """
        Get historical weather data for a city on a specific date.
        Requires 'date' query parameter in YYYY-MM-DD format.
        """
        # Get the city
        try:
            city = City.objects.get(uuid=city_uuid)
        except City.DoesNotExist:
            return Response(
                {'detail': 'City not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get date parameter
        date_str = request.query_params.get('date')
        if not date_str:
            return Response(
                {'detail': 'Date parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Try to get historical data
        try:
            historical = WeatherHistory.objects.get(city=city, date=date_str)
        except WeatherHistory.DoesNotExist:
            return Response(
                {'detail': f'No historical weather data found for {city.name} on {date_str}.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = WeatherHistorySerializer(historical)
        return Response(serializer.data)

    def create(self, request, city_uuid=None):
        """
        Create historical weather data for a city.
        """
        # Get the city
        try:
            city = City.objects.get(uuid=city_uuid)
        except City.DoesNotExist:
            return Response(
                {'detail': 'City not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = WeatherHistoryCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Check if data for this date already exists
            date = serializer.validated_data['date']
            if WeatherHistory.objects.filter(city=city, date=date).exists():
                # Update existing record
                historical = WeatherHistory.objects.get(city=city, date=date)
                for key, value in serializer.validated_data.items():
                    setattr(historical, key, value)
                historical.save()
            else:
                # Create new record
                historical = WeatherHistory.objects.create(
                    city=city,
                    **serializer.validated_data
                )

            response_serializer = WeatherHistorySerializer(historical)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
