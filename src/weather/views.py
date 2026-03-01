from datetime import datetime

from rest_framework import filters, status, viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from src.weather.models import City, CurrentWeather, WeatherForecast
from src.weather.serializers import CitySerializer, CurrentWeatherSerializer, WeatherForecastSerializer


class IsAdminUser(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_staff


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]

    def list(self, request, *args, **kwargs):
        search_name = request.query_params.get('search_name')
        if search_name:
            queryset = self.queryset.filter(name__icontains=search_name)
        else:
            queryset = self.queryset.all()

        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CurrentWeatherViewSet(viewsets.ModelViewSet):
    queryset = CurrentWeather.objects.all()
    serializer_class = CurrentWeatherSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class HistoricalWeatherViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CurrentWeather.objects.all()
    serializer_class = CurrentWeatherSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        city_name = request.query_params.get('city')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        queryset = self.queryset.all()
        if city_name:
            queryset = queryset.filter(city__name=city_name)
        if start_date and end_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
            queryset = queryset.filter(timestamp__gte=start_datetime, timestamp__lte=end_datetime)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class WeatherForecastViewSet(viewsets.ModelViewSet):
    queryset = WeatherForecast.objects.all()
    serializer_class = WeatherForecastSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
