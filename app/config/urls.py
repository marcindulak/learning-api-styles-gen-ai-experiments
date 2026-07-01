"""URL configuration for the Weather Forecast Service."""
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

from config.views import health
from weather.schema import schema
from weather.views import CityDetailView, CityListView, CityWeatherView

urlpatterns = [
    path("api/health", health, name="health"),
    path("api/cities", CityListView.as_view(), name="city-list"),
    path("api/cities/<uuid:uuid>", CityDetailView.as_view(), name="city-detail"),
    path(
        "api/cities/<uuid:uuid>/weather",
        CityWeatherView.as_view(),
        name="city-weather",
    ),
    path(
        "graphql",
        csrf_exempt(GraphQLView.as_view(schema=schema, graphiql=True)),
        name="graphql",
    ),
]
