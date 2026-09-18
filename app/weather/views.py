from rest_framework.response import Response
from rest_framework.views import APIView

from .models import WeatherRecord
from .serializers import WeatherRecordSerializer


class CurrentWeatherView(APIView):
    def get(self, request, city_uuid):
        try:
            record = WeatherRecord.objects.filter(city__uuid=city_uuid).latest()
        except WeatherRecord.DoesNotExist:
            return Response(status=404)
        return Response(WeatherRecordSerializer(record).data)
