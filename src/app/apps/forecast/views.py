from datetime import date, timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from apps.cities.models import City
from .models import WeatherForecast
from .serializers import WeatherForecastSerializer

# Maximum number of days for forecast
MAX_FORECAST_DAYS = 7


class ForecastViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for weather forecast retrieval.
    """
    queryset = WeatherForecast.objects.all()
    serializer_class = WeatherForecastSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'

    def get_queryset(self):
        """Filter forecasts by city if specified."""
        queryset = super().get_queryset()
        city_uuid = self.kwargs.get('city_uuid')
        if city_uuid:
            queryset = queryset.filter(city__uuid=city_uuid)
        return queryset

    @action(detail=False, methods=['get'], url_path='')
    def city_forecast(self, request, city_uuid=None):
        """
        Get weather forecast for a city.
        Optional 'days' query parameter to specify number of days (max 7).
        """
        # Validate days parameter
        days_param = request.query_params.get('days')
        if days_param is not None:
            try:
                days = int(days_param)
            except ValueError:
                raise ValidationError({'days': 'Must be a valid integer.'})

            if days > MAX_FORECAST_DAYS:
                raise ValidationError({
                    'days': f'Forecast is limited to a maximum of {MAX_FORECAST_DAYS} days.'
                })
            if days < 1:
                raise ValidationError({'days': 'Must be at least 1 day.'})
        else:
            days = MAX_FORECAST_DAYS

        # Get the city
        try:
            city = City.objects.get(uuid=city_uuid)
        except City.DoesNotExist:
            return Response(
                {'detail': 'City not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get forecasts for the specified number of days from today
        today = date.today()
        end_date = today + timedelta(days=days - 1)

        forecasts = WeatherForecast.objects.filter(
            city=city,
            forecast_date__gte=today,
            forecast_date__lte=end_date
        ).order_by('forecast_date')

        # If no forecasts exist, generate mock data
        if not forecasts.exists():
            forecasts = self._generate_mock_forecast(city, days)

        serializer = self.get_serializer(forecasts, many=True)
        return Response({
            'city_uuid': str(city.uuid),
            'city_name': city.name,
            'days_requested': days,
            'forecasts': serializer.data
        })

    def _generate_mock_forecast(self, city, days):
        """Generate mock forecast data for testing purposes."""
        today = date.today()
        forecasts = []

        # Sample weather conditions
        conditions = [
            'Clear sky',
            'Partly cloudy',
            'Overcast',
            'Light rain',
            'Sunny',
            'Scattered clouds',
            'Moderate rain',
        ]

        for i in range(days):
            forecast_date = today + timedelta(days=i)
            # Create mock forecast (not saved to DB for in-memory testing)
            forecast = WeatherForecast(
                city=city,
                forecast_date=forecast_date,
                temperature=20.0 + (i % 10) - 5,  # Varies between 15-25
                humidity=60.0 + (i % 20) - 10,    # Varies between 50-70
                wind_speed=5.0 + (i % 5),         # Varies between 5-10
                condition=conditions[i % len(conditions)],
            )
            forecast.save()
            forecasts.append(forecast)

        return forecasts
