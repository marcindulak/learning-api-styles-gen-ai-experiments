from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import City
from .serializers import CitySerializer

# Maximum number of cities allowed in the system
MAX_CITIES = 5


class CityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for City management.
    Provides CRUD operations for cities with proper permission checks.
    """
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name']
    filterset_fields = ['country', 'region']

    def perform_create(self, serializer):
        """Only admin users can create cities, limited to MAX_CITIES."""
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admin users can create cities.")

        # Check if we've reached the maximum number of cities
        current_count = City.objects.count()
        if current_count >= MAX_CITIES:
            raise ValidationError(
                f"Cannot create more than {MAX_CITIES} cities. Current count: {current_count}."
            )

        serializer.save()

    def perform_update(self, serializer):
        """Only admin users can update cities."""
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admin users can update cities.")
        serializer.save()

    def perform_destroy(self, instance):
        """Only admin users can delete cities (but not predefined ones)."""
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admin users can delete cities.")

        # Prevent deletion if this would drop below MAX_CITIES (predefined cities protection)
        current_count = City.objects.count()
        if current_count <= MAX_CITIES:
            raise PermissionDenied(
                f"Cannot delete predefined cities. Minimum {MAX_CITIES} cities required."
            )

        instance.delete()
