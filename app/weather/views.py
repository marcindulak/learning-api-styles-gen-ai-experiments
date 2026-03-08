"""
Views for weather API endpoints.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from weather.models import City
from weather.serializers import CitySerializer


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
