"""URL configuration for Weather Forecast Service."""
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from graphene_django.views import GraphQLView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/jwt/obtain', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/jwt/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('weather.urls')),
    path('graphql', csrf_exempt(GraphQLView.as_view(graphiql=True))),
    # OpenAPI schema and documentation
    path('api/schema', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
