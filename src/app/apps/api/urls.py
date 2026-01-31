from django.urls import path, include

app_name = 'api'

urlpatterns = [
    # Authentication
    path('', include('apps.authentication.urls')),

    # Cities
    path('cities', include('apps.cities.urls')),

    # Forecast
    path('cities', include('apps.forecast.urls')),

    # Historical
    path('cities', include('apps.historical.urls')),

    # Weather
    path('cities', include('apps.weather.urls')),
]
