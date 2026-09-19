from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.renderers import OpenApiJsonRenderer
from drf_spectacular.views import SpectacularAPIView
from rest_framework_simplejwt.views import TokenObtainPairView
from strawberry.django.views import GraphQLView

from weather.schema import schema

from .views import AsyncAPISchemaView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("weather.urls")),
    path("api/", include("webhooks.urls")),
    path("api/jwt/obtain", TokenObtainPairView.as_view(), name="jwt-obtain"),
    path("api/graphql", csrf_exempt(GraphQLView.as_view(schema=schema))),
    # Forced to JSON regardless of the request's Accept header: drf-spectacular's
    # own default (YAML when unspecified) is a poor default for this project,
    # since every schema consumer here (BDD steps, curl, /api/async-schema)
    # already expects JSON, and nothing serves or parses YAML elsewhere.
    path("api/schema", SpectacularAPIView.as_view(renderer_classes=[OpenApiJsonRenderer]), name="openapi-schema"),
    path("api/async-schema", AsyncAPISchemaView.as_view(), name="asyncapi-schema"),
]
