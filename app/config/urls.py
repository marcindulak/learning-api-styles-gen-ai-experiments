"""
URL configuration for Weather Forecast Service project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from strawberry.django.views import GraphQLView
from weather.schema import schema
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    # JWT authentication endpoints
    path('api/jwt/obtain', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/jwt/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    # GraphQL endpoint with GraphiQL UI (enabled by default)
    path('api/graphql/', GraphQLView.as_view(schema=schema), name='graphql'),
    # API Documentation (drf-spectacular)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # Weather API endpoints
    path('api/', include('weather.urls')),
]
