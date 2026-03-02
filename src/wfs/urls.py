"""
URL configuration for Weather Forecast Service project.
"""
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from src.weather.views import ForecastAtomFeed, GitHubWebhookView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/jwt/obtain', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/jwt/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('src.weather.urls')),
    path('graphql', csrf_exempt(GraphQLView.as_view(graphiql=True)), name='graphql'),
    path('feeds/forecast/<str:city_name>/', ForecastAtomFeed(), name='forecast_feed'),
    path('webhooks/github', csrf_exempt(GitHubWebhookView.as_view()), name='github_webhook'),
]
