"""Weather views."""
from rest_framework import filters, permissions, viewsets

from .models import City, WeatherAlert, WeatherForecast, WeatherRecord
from .serializers import (
    CitySerializer,
    WeatherAlertSerializer,
    WeatherForecastSerializer,
    WeatherRecordSerializer,
)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow admins to edit objects."""

    def has_permission(self, request, view) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class CityViewSet(viewsets.ModelViewSet):
    """City viewset."""

    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'country', 'region']
    lookup_field = 'uuid'

    def get_queryset(self):
        """Filter cities by search_name parameter if provided."""
        queryset = City.objects.all()
        search_name = self.request.query_params.get('search_name', None)
        if search_name is not None:
            queryset = queryset.filter(name__icontains=search_name)
        return queryset


class WeatherRecordViewSet(viewsets.ModelViewSet):
    """Weather record viewset."""

    queryset = WeatherRecord.objects.select_related('city').all()
    serializer_class = WeatherRecordSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['city__name']
    lookup_field = 'uuid'

    def get_queryset(self):
        """Filter weather records by city if provided."""
        queryset = WeatherRecord.objects.select_related('city').all()
        city_uuid = self.request.query_params.get('city_uuid', None)
        if city_uuid is not None:
            queryset = queryset.filter(city__uuid=city_uuid)
        return queryset


class WeatherForecastViewSet(viewsets.ModelViewSet):
    """Weather forecast viewset."""

    queryset = WeatherForecast.objects.select_related('city').all()
    serializer_class = WeatherForecastSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['city__name']
    lookup_field = 'uuid'

    def get_queryset(self):
        """Filter weather forecasts by city if provided."""
        queryset = WeatherForecast.objects.select_related('city').all()
        city_uuid = self.request.query_params.get('city_uuid', None)
        if city_uuid is not None:
            queryset = queryset.filter(city__uuid=city_uuid)
        return queryset


class WeatherAlertViewSet(viewsets.ModelViewSet):
    """Weather alert viewset."""

    queryset = WeatherAlert.objects.select_related('city').all()
    serializer_class = WeatherAlertSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['city__name', 'alert_type']
    lookup_field = 'uuid'

    def get_queryset(self):
        """Filter weather alerts by city and active status if provided."""
        queryset = WeatherAlert.objects.select_related('city').all()
        city_uuid = self.request.query_params.get('city_uuid', None)
        if city_uuid is not None:
            queryset = queryset.filter(city__uuid=city_uuid)
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset
