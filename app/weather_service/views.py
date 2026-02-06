from django.http import HttpResponse
from django.utils import timezone
from django.utils.feedgenerator import Atom1Feed
from django.views import View
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from weather_service.models import City, WeatherForecast, WeatherRecord
from weather_service.serializers import (
    CitySerializer,
    WeatherForecastSerializer,
    WeatherRecordSerializer,
)


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
