from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from strawberry.django.views import GraphQLView

from weather.schema import schema

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("weather.urls")),
    path("api/", include("webhooks.urls")),
    path("api/graphql", csrf_exempt(GraphQLView.as_view(schema=schema))),
]
