"""
URL configuration for Weather Forecast Service project.
"""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from weather.graphql_views import PublicGraphQLView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/jwt/obtain', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/jwt/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('weather.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('graphql', PublicGraphQLView.as_view(graphiql=True)),
]
