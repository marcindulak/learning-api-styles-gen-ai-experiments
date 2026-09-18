from datetime import date

from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import City, Forecast, WeatherRecord
from .permissions import IsAdminOrReadOnly, IsSelfOrAdmin
from .serializers import (
    CitySerializer,
    ForecastSerializer,
    HistoricalWeatherRecordSerializer,
    UserSerializer,
    WeatherRecordSerializer,
)


# Unlike this file's other views, listing/creating a City needs no custom
# query-param parsing or filtering, so DRF's generic covers it exactly as
# written; the other views stay hand-rolled because they do have custom
# logic the generic can't express.
class CityListCreateView(generics.ListCreateAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAdminOrReadOnly]


class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "username"
    permission_classes = [IsAuthenticated, IsSelfOrAdmin]


class CurrentWeatherView(APIView):
    def get(self, request, city_uuid):
        try:
            record = WeatherRecord.objects.filter(city__uuid=city_uuid).latest()
        except WeatherRecord.DoesNotExist:
            return Response(status=404)
        return Response(WeatherRecordSerializer(record).data)


class HistoricalWeatherView(APIView):
    # Query params are parsed by hand rather than through a DRF Serializer:
    # no endpoint in this codebase validates query params via a Serializer
    # yet, and two date fields don't justify introducing that pattern ahead
    # of a second consumer (AHA - avoid hasty abstractions).
    def get(self, request, city_uuid):
        try:
            start = date.fromisoformat(request.query_params["start"])
            end = date.fromisoformat(request.query_params["end"])
        except (KeyError, ValueError):
            return Response(status=400)
        if start > end:
            return Response(status=400)
        records = WeatherRecord.objects.filter(
            city__uuid=city_uuid, recorded_at__date__range=(start, end)
        ).order_by("recorded_at")
        return Response(HistoricalWeatherRecordSerializer(records, many=True).data)


class ForecastView(APIView):
    # Query params are parsed by hand, matching HistoricalWeatherView above:
    # a single bounded integer param doesn't justify a DRF Serializer-based
    # validator when no endpoint in this codebase uses that pattern yet.
    def get(self, request, city_uuid):
        try:
            days = int(request.query_params["days"])
        except (KeyError, ValueError):
            return Response(status=400)
        if not 1 <= days <= 7:
            return Response({"error": "the maximum is 7 days"}, status=400)
        # Forecast.Meta.ordering = ["date"] already orders these ascending.
        forecasts = Forecast.objects.filter(city__uuid=city_uuid)[:days]
        return Response(ForecastSerializer(forecasts, many=True).data)
