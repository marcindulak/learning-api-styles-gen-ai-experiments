from django.urls import path
from .views import ForecastViewSet

app_name = 'forecast'

forecast_view = ForecastViewSet.as_view({
    'get': 'city_forecast',
})

urlpatterns = [
    path('/<uuid:city_uuid>/forecast', forecast_view, name='city-forecast'),
]
