from django.urls import path, include

app_name = 'api'

urlpatterns = [
    # Authentication
    path('', include('apps.authentication.urls')),

    # Cities
    path('cities/', include('apps.cities.urls')),

    # Weather
    path('weather/', include('apps.weather.urls')),

    # Feeds
    path('feeds/', include('apps.feeds.urls')),

    # Webhooks
    path('webhooks/', include('apps.webhooks.urls')),
]
