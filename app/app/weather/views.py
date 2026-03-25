import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import City, WeatherRecord, WeatherForecast, WeatherAlert
from .permissions import IsAdminOrReadOnly
from .serializers import (
    CitySerializer, WeatherRecordSerializer,
    WeatherForecastSerializer, WeatherAlertSerializer,
)

logger = logging.getLogger(__name__)


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "country", "region"]
    ordering_fields = ["name", "country"]
    lookup_field = "uuid"

    def get_queryset(self):
        qs = super().get_queryset()
        search_name = self.request.query_params.get("search_name")
        if search_name:
            qs = qs.filter(name__icontains=search_name)
        return qs

    @action(detail=True, methods=["get"], url_path="forecasts")
    def forecasts(self, request, uuid=None):
        city = self.get_object()
        forecasts = city.forecasts.all()
        serializer = WeatherForecastSerializer(forecasts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="records")
    def records(self, request, uuid=None):
        city = self.get_object()
        records = city.weather_records.all()
        serializer = WeatherRecordSerializer(records, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="import-forecast")
    def import_forecast(self, request, uuid=None):
        """Import 7-day forecast from Open-Meteo for this city."""
        from .services import fetch_and_store_forecast
        city = self.get_object()
        try:
            count = fetch_and_store_forecast(city)
            return Response({"imported": count})
        except Exception:
            logger.exception("Failed to import forecast for city %s", city.uuid)
            return Response(
                {"error": "Failed to import forecast"},
                status=status.HTTP_502_BAD_GATEWAY,
            )


class WeatherRecordViewSet(viewsets.ModelViewSet):
    queryset = WeatherRecord.objects.select_related("city").all()
    serializer_class = WeatherRecordSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["city__name"]
    ordering_fields = ["recorded_at", "temperature_celsius"]
    lookup_field = "uuid"


class WeatherForecastViewSet(viewsets.ModelViewSet):
    queryset = WeatherForecast.objects.select_related("city").all()
    serializer_class = WeatherForecastSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["city__name"]
    ordering_fields = ["forecast_date"]
    lookup_field = "uuid"


class WeatherAlertViewSet(viewsets.ModelViewSet):
    queryset = WeatherAlert.objects.select_related("city", "created_by").all()
    serializer_class = WeatherAlertSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["city__name", "title"]
    ordering_fields = ["issued_at", "severity"]
    lookup_field = "uuid"

    def perform_create(self, serializer):
        alert = serializer.save(created_by=self.request.user)
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"alerts_{alert.city.uuid}",
                {
                    "type": "alert.message",
                    "uuid": str(alert.uuid),
                    "city": alert.city.name,
                    "severity": alert.severity,
                    "title": alert.title,
                    "message": alert.message,
                    "issued_at": alert.issued_at.isoformat(),
                },
            )
        except Exception:
            logger.exception("Failed to broadcast alert %s via WebSocket", alert.uuid)


@method_decorator(csrf_exempt, name="dispatch")
class GitHubWebhookView(View):
    """Receive GitHub webhook events and log them."""

    def post(self, request):
        signature = request.headers.get("X-Hub-Signature-256", "")
        secret = settings.WEBHOOK_SECRET.encode()
        digest = "sha256=" + hmac.new(secret, request.body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, digest):
            return JsonResponse({"error": "Invalid signature"}, status=403)

        event = request.headers.get("X-GitHub-Event", "unknown")
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        logger.info("GitHub webhook received: event=%s, action=%s", event, payload.get("action", "n/a"))
        return JsonResponse({"received": True, "event": event})
