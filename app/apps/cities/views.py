from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from .models import City
from .serializers import CitySerializer


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
        """Only admin users can create cities."""
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admin users can create cities.")
        serializer.save()

    def perform_update(self, serializer):
        """Only admin users can update cities."""
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admin users can update cities.")
        serializer.save()

    def perform_destroy(self, instance):
        """Only admin users can delete cities."""
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admin users can delete cities.")
        instance.delete()
