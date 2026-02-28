"""DRF views for the Weather Forecast Service."""

import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.db import connection
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import City, WeatherAlert, WeatherForecast, WeatherRecord
from .permissions import IsAdminOrReadOnly
from .serializers import (
    CitySerializer,
    WeatherAlertSerializer,
    WeatherForecastSerializer,
    WeatherRecordSerializer,
)

logger = logging.getLogger(__name__)


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "uuid"

    def get_queryset(self):
        qs = super().get_queryset()
        search_name = self.request.query_params.get("search_name")
        if search_name:
            qs = qs.filter(name__icontains=search_name)
        return qs


class WeatherRecordViewSet(viewsets.ModelViewSet):
    serializer_class = WeatherRecordSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "uuid"
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        city_uuid = self.kwargs["city_uuid"]
        qs = WeatherRecord.objects.filter(city__uuid=city_uuid)
        from_date = self.request.query_params.get("from")
        to_date = self.request.query_params.get("to")
        if from_date:
            qs = qs.filter(timestamp__gte=from_date)
        if to_date:
            qs = qs.filter(timestamp__lte=to_date)
        return qs

    def create(self, request, *args, **kwargs):
        city = get_object_or_404(City, uuid=self.kwargs["city_uuid"])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(city=city)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        get_object_or_404(City, uuid=self.kwargs["city_uuid"])
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        get_object_or_404(City, uuid=self.kwargs["city_uuid"])
        return super().retrieve(request, *args, **kwargs)


class WeatherForecastViewSet(viewsets.ModelViewSet):
    serializer_class = WeatherForecastSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "uuid"
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        city_uuid = self.kwargs["city_uuid"]
        return WeatherForecast.objects.filter(city__uuid=city_uuid)

    def create(self, request, *args, **kwargs):
        city = get_object_or_404(City, uuid=self.kwargs["city_uuid"])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(city=city)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        get_object_or_404(City, uuid=self.kwargs["city_uuid"])
        return super().list(request, *args, **kwargs)


class WeatherAlertViewSet(viewsets.ModelViewSet):
    serializer_class = WeatherAlertSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "uuid"
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        qs = WeatherAlert.objects.all()
        city_uuid = self.request.query_params.get("city")
        severity = self.request.query_params.get("severity")
        if city_uuid:
            qs = qs.filter(city__uuid=city_uuid)
        if severity:
            qs = qs.filter(severity=severity)
        # Default to active only
        active = self.request.query_params.get("active")
        if active is None:
            qs = qs.filter(active=True)
        elif active.lower() in ("true", "1"):
            qs = qs.filter(active=True)
        elif active.lower() in ("false", "0"):
            qs = qs.filter(active=False)
        return qs


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint."""
    try:
        connection.ensure_connection()
        return Response({"status": "ok"}, status=status.HTTP_200_OK)
    except Exception:
        return Response(
            {"status": "error", "detail": "Database unavailable"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def github_webhook(request):
    """GitHub webhook handler with HMAC-SHA256 signature verification."""
    signature_header = request.headers.get("X-Hub-Signature-256", "")
    if not signature_header:
        return Response(
            {"detail": "Invalid signature"}, status=status.HTTP_403_FORBIDDEN
        )

    secret = settings.WEBHOOK_SECRET.encode("utf-8")
    expected_signature = (
        "sha256="
        + hmac.new(secret, request.body, hashlib.sha256).hexdigest()
    )

    if not hmac.compare_digest(signature_header, expected_signature):
        return Response(
            {"detail": "Invalid signature"}, status=status.HTTP_403_FORBIDDEN
        )

    event_type = request.headers.get("X-GitHub-Event", "unknown")
    logger.info("GitHub webhook received: event=%s", event_type)

    if event_type == "ping":
        return Response({"status": "pong"}, status=status.HTTP_200_OK)

    if event_type == "push":
        payload = json.loads(request.body)
        commits = payload.get("commits", [])
        logger.info(
            "Push event: %d commit(s) to %s",
            len(commits),
            payload.get("ref", "unknown"),
        )

    return Response({"status": "ok"}, status=status.HTTP_200_OK)
