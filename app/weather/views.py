from datetime import date

from rest_framework.response import Response
from rest_framework.views import APIView

from .models import WeatherRecord
from .serializers import HistoricalWeatherRecordSerializer, WeatherRecordSerializer


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
