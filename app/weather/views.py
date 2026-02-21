from datetime import datetime
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from .models import City, WeatherRecord, Forecast
from .serializers import CitySerializer, WeatherRecordSerializer, ForecastSerializer
from .permissions import IsAdminOrReadOnly


class CityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for City CRUD operations.
    Admin users: full CRUD access
    Regular users: read-only access
    """
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'uuid'

    def get_queryset(self):
        """Filter cities by search_name query parameter."""
        queryset = City.objects.all()
        search_name = self.request.query_params.get('search_name', None)

        if search_name:
            queryset = queryset.filter(name__icontains=search_name)

        return queryset


class WeatherRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for WeatherRecord operations.
    Admin users: full CRUD access
    Regular users: read-only access (list/retrieve)
    """
    queryset = WeatherRecord.objects.all()
    serializer_class = WeatherRecordSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'uuid'

    def get_queryset(self):
        """Filter by city and date range."""
        queryset = WeatherRecord.objects.all().order_by('-recorded_at')

        # Filter by city UUID
        city_uuid = self.request.query_params.get('city', None)
        if city_uuid:
            queryset = queryset.filter(city__uuid=city_uuid)

        # Filter by date range
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)

        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                queryset = queryset.filter(recorded_at__gte=date_from_obj)
            except ValueError:
                raise ValidationError({'date_from': 'Invalid date format. Use YYYY-MM-DD.'})

        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                queryset = queryset.filter(recorded_at__lte=date_to_obj)
            except ValueError:
                raise ValidationError({'date_to': 'Invalid date format. Use YYYY-MM-DD.'})

        return queryset


class ForecastViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Forecast operations.
    All authenticated users: list/retrieve
    Admin users: create/update/delete
    """
    queryset = Forecast.objects.all()
    serializer_class = ForecastSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'uuid'

    def get_queryset(self):
        """Filter by city UUID."""
        queryset = Forecast.objects.all().order_by('forecast_date')

        city_uuid = self.request.query_params.get('city', None)
        if city_uuid:
            queryset = queryset.filter(city__uuid=city_uuid)

        return queryset
