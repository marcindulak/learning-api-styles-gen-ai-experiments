import hashlib
import hmac
import json
import os
from datetime import datetime

from django.contrib.syndication.views import Feed
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.feedgenerator import Atom1Feed
from django.views.decorators.csrf import csrf_exempt
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from src.weather.models import City, CurrentWeather, WeatherAlert, WebhookEvent, WeatherForecast
from src.weather.serializers import CitySerializer, CurrentWeatherSerializer, WeatherAlertSerializer, WeatherForecastSerializer
from src.weather.services import WeatherAPIException, weather_api_service


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
    lookup_field = 'city__name'
    lookup_value_regex = '[^/]+'

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return []

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.select_related('city')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        city_name = kwargs.get('city__name')
        city = get_object_or_404(City, name=city_name)
        weather = CurrentWeather.objects.filter(city=city).order_by('-timestamp').first()

        if not weather:
            return Response(
                {'detail': f'No current weather data found for city: {city_name}'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(weather)
        return Response(serializer.data)

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
    lookup_field = 'city__name'
    lookup_value_regex = '[^/]+'

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return []

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.select_related('city')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        city_name = kwargs.get('city__name')
        city = get_object_or_404(City, name=city_name)
        forecasts = WeatherForecast.objects.filter(city=city).order_by('forecast_date')

        if not forecasts.exists():
            return Response(
                {'detail': f'No forecast data found for city: {city_name}'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(forecasts, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WeatherAlertViewSet(viewsets.ModelViewSet):
    queryset = WeatherAlert.objects.all()
    serializer_class = WeatherAlertSerializer

    def get_permissions(self):
        return []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SetTestModeView(APIView):
    """Internal endpoint to set weather API test mode."""
    permission_classes = []

    def post(self, request):
        import os
        test_mode = request.data.get('test_mode')
        if test_mode:
            os.environ['WEATHER_API_TEST_MODE'] = test_mode
            return Response({'message': f'Test mode set to {test_mode}'}, status=status.HTTP_200_OK)
        else:
            os.environ.pop('WEATHER_API_TEST_MODE', None)
            return Response({'message': 'Test mode cleared'}, status=status.HTTP_200_OK)


class SetEnvironmentView(APIView):
    """Internal endpoint to set environment variables for testing."""
    permission_classes = []

    def post(self, request):
        import os
        for key, value in request.data.items():
            if value:
                os.environ[key] = value
            else:
                os.environ.pop(key, None)
        return Response({'message': 'Environment variables set'}, status=status.HTTP_200_OK)


class FetchWeatherView(APIView):
    """Admin endpoint to fetch weather data from third-party API."""
    permission_classes = [IsAdminUser]

    def post(self, request):
        city_name = request.data.get('city_name')
        data_type = request.data.get('data_type')

        if not city_name or not data_type:
            return Response(
                {'error': 'city_name and data_type are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            city = City.objects.get(name=city_name)
        except City.DoesNotExist:
            return Response(
                {'error': f'City {city_name} not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            if data_type == 'current':
                weather = weather_api_service.fetch_current_weather(city)
                weather.save()
                return Response(
                    {'message': f'Current weather data fetched for {city_name}'},
                    status=status.HTTP_200_OK
                )
            elif data_type == 'forecast':
                forecasts = weather_api_service.fetch_forecast(city)
                for forecast in forecasts:
                    forecast.save()
                return Response(
                    {'message': f'Forecast data fetched for {city_name}'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'data_type must be "current" or "forecast"'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except WeatherAPIException as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class ForecastAtomFeed(Feed):
    """Atom feed for weather forecasts for a specific city."""
    feed_type = Atom1Feed

    def get_object(self, request, city_name):
        try:
            return City.objects.get(name=city_name)
        except City.DoesNotExist:
            raise Http404(f"City '{city_name}' not found")

    def title(self, obj):
        return f"Weather Forecast for {obj.name}"

    def link(self, obj):
        return f"/feeds/forecast/{obj.name}"

    def description(self, obj):
        return f"7-day weather forecast for {obj.name}, {obj.country}"

    def items(self, obj):
        return WeatherForecast.objects.filter(city=obj).order_by('forecast_date')[:7]

    def item_title(self, item):
        return f"Weather forecast for {item.city.name} on {item.forecast_date}"

    def item_description(self, item):
        return (
            f"Temperature: {item.temperature}°C, "
            f"Humidity: {item.humidity}%, "
            f"Pressure: {item.pressure} hPa, "
            f"Wind Speed: {item.wind_speed} m/s, "
            f"Conditions: {item.conditions}"
        )

    def item_link(self, item):
        return f"/api/weather/forecast/{item.city.name}"

    def item_updateddate(self, item):
        return item.created_at


class GitHubWebhookView(APIView):
    """Endpoint to receive GitHub webhook events."""
    permission_classes = []

    def _verify_signature(self, payload_body: bytes, signature_header: str) -> bool:
        """Verify the GitHub webhook signature using HMAC-SHA256."""
        webhook_secret = os.environ.get('GITHUB_WEBHOOK_SECRET', '')
        if not webhook_secret:
            return True

        if not signature_header or not signature_header.startswith('sha256='):
            return False

        expected_signature = signature_header[7:]
        computed_signature = hmac.new(
            webhook_secret.encode(),
            payload_body,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(computed_signature, expected_signature)

    def _trigger_data_refresh(self):
        """Trigger weather data fetch for all cities."""
        cities = City.objects.all()
        for city in cities:
            try:
                current_weather = weather_api_service.fetch_current_weather(city)
                current_weather.save()
                forecasts = weather_api_service.fetch_forecast(city)
                for forecast in forecasts:
                    forecast.save()
            except WeatherAPIException:
                pass

    def post(self, request):
        payload_body = request.body
        signature_header = request.META.get('HTTP_X_HUB_SIGNATURE_256', '')

        webhook_secret = os.environ.get('GITHUB_WEBHOOK_SECRET', '')
        if webhook_secret:
            if not self._verify_signature(payload_body, signature_header):
                return Response(
                    {'error': 'Invalid signature'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        try:
            payload = json.loads(payload_body.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return Response(
                {'error': 'Invalid JSON payload'},
                status=status.HTTP_400_BAD_REQUEST
            )

        event_type = request.META.get('HTTP_X_GITHUB_EVENT', 'push')

        webhook_event = WebhookEvent(
            event_type=event_type,
            payload=payload,
            processed=False
        )
        webhook_event.save()

        ref = payload.get('ref', '')
        if 'data-refresh' in ref or payload.get('head_commit', {}).get('message', '').startswith('[data-refresh]'):
            self._trigger_data_refresh()

        webhook_event.processed = True
        webhook_event.save()

        return Response(
            {'message': 'Webhook received'},
            status=status.HTTP_200_OK
        )


class AsyncAPISchemaView(APIView):
    """Endpoint to provide AsyncAPI schema for WebSocket documentation."""
    permission_classes = []

    def get(self, request):
        schema = {
            "asyncapi": "2.6.0",
            "info": {
                "title": "Weather Forecast Service WebSocket API",
                "version": "1.0.0",
                "description": "Real-time weather alerts via WebSocket"
            },
            "servers": {
                "production": {
                    "url": "ws://localhost:8000",
                    "protocol": "ws",
                    "description": "WebSocket server for weather alerts"
                }
            },
            "channels": {
                "/ws/alerts": {
                    "description": "WebSocket channel for receiving weather alerts",
                    "subscribe": {
                        "summary": "Subscribe to weather alerts for cities",
                        "message": {
                            "$ref": "#/components/messages/AlertMessage"
                        }
                    },
                    "publish": {
                        "summary": "Send subscription commands",
                        "message": {
                            "$ref": "#/components/messages/SubscriptionCommand"
                        }
                    }
                }
            },
            "components": {
                "messages": {
                    "AlertMessage": {
                        "name": "AlertMessage",
                        "title": "Weather Alert",
                        "summary": "Weather alert notification for a city",
                        "contentType": "application/json",
                        "payload": {
                            "$ref": "#/components/schemas/Alert"
                        }
                    },
                    "SubscriptionCommand": {
                        "name": "SubscriptionCommand",
                        "title": "Subscription Command",
                        "summary": "Command to subscribe or unsubscribe from city alerts",
                        "contentType": "application/json",
                        "payload": {
                            "$ref": "#/components/schemas/Command"
                        }
                    }
                },
                "schemas": {
                    "Alert": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["alert"],
                                "description": "Message type"
                            },
                            "city": {
                                "type": "string",
                                "description": "City name for the alert"
                            },
                            "severity": {
                                "type": "string",
                                "description": "Alert severity level"
                            },
                            "message": {
                                "type": "string",
                                "description": "Alert message content"
                            }
                        },
                        "required": ["type", "city", "severity", "message"]
                    },
                    "Command": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["subscribe", "unsubscribe"],
                                "description": "Command type"
                            },
                            "city": {
                                "type": "string",
                                "description": "City name to subscribe/unsubscribe"
                            }
                        },
                        "required": ["type", "city"]
                    }
                }
            }
        }
        return JsonResponse(schema)
