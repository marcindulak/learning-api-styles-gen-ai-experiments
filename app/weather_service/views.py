import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.feedgenerator import Atom1Feed
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from weather_service.models import City, WeatherForecast, WeatherRecord
from weather_service.serializers import (
    CitySerializer,
    WeatherForecastSerializer,
    WeatherRecordSerializer,
)

logger = logging.getLogger(__name__)


class CityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for City model.
    Provides CRUD operations for cities.
    """

    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = "uuid"
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


class WeatherRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for WeatherRecord model.
    Provides CRUD operations for weather records.
    """

    queryset = WeatherRecord.objects.all()
    serializer_class = WeatherRecordSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["city__name"]


class WeatherForecastViewSet(viewsets.ModelViewSet):
    """
    ViewSet for WeatherForecast model.
    Provides CRUD operations for weather forecasts.
    """

    queryset = WeatherForecast.objects.all()
    serializer_class = WeatherForecastSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["city__name"]


class WeatherForecastAtomFeedView(View):
    """
    View that generates an Atom feed for weather forecasts.
    """

    def get(self, request):
        feed = Atom1Feed(
            title="Weather Forecast Feed",
            link=request.build_absolute_uri("/api/feed/forecast"),
            description="Weather forecasts for cities",
            language="en",
            author_name="Weather Forecast Service",
        )

        forecasts = WeatherForecast.objects.select_related("city").order_by("-created_at")

        if forecasts.exists():
            latest_forecast = forecasts.first()
            feed.feed["updated"] = latest_forecast.created_at
        else:
            feed.feed["updated"] = timezone.now()

        for forecast in forecasts:
            feed.add_item(
                title=f"Weather forecast for {forecast.city.name}",
                link=request.build_absolute_uri(f"/api/forecasts/{forecast.id}"),
                description=f"Temperature: {forecast.temperature}°C, Humidity: {forecast.humidity}%, Pressure: {forecast.pressure} hPa",
                pubdate=forecast.created_at,
                unique_id=f"forecast-{forecast.id}",
            )

        response = HttpResponse(content_type="application/atom+xml; charset=utf-8")
        feed.write(response, "utf-8")
        return response


@method_decorator(csrf_exempt, name="dispatch")
class GitHubWebhookView(View):
    """
    View that handles GitHub webhook events.
    """

    def post(self, request):
        payload_body = request.body
        signature_header = request.headers.get("X-Hub-Signature-256", "")
        event_type = request.headers.get("X-GitHub-Event", "")

        if settings.GITHUB_WEBHOOK_SECRET:
            if not self._verify_signature(payload_body, signature_header):
                logger.warning("GitHub webhook signature verification failed")
                return JsonResponse({"error": "Invalid signature"}, status=401)

        try:
            payload = json.loads(payload_body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        if event_type == "push":
            logger.info(f"Received GitHub push event: {payload.get('ref', 'unknown')}")
        elif event_type == "issues":
            action = payload.get("action", "unknown")
            issue_number = payload.get("issue", {}).get("number", "unknown")
            logger.info(f"Received GitHub issue {action} event: #{issue_number}")
        elif event_type == "pull_request":
            action = payload.get("action", "unknown")
            pr_number = payload.get("pull_request", {}).get("number", "unknown")
            logger.info(f"Received GitHub pull request {action} event: #{pr_number}")
        else:
            logger.info(f"Received GitHub {event_type} event")

        return JsonResponse({"status": "success"}, status=200)

    def _verify_signature(self, payload_body: bytes, signature_header: str) -> bool:
        """
        Verify the HMAC-SHA256 signature from GitHub.
        """
        if not signature_header.startswith("sha256="):
            return False

        expected_signature = signature_header[7:]
        secret = settings.GITHUB_WEBHOOK_SECRET.encode("utf-8")
        computed_signature = hmac.new(secret, payload_body, hashlib.sha256).hexdigest()

        return hmac.compare_digest(computed_signature, expected_signature)
