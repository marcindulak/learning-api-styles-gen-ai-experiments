from django.urls import path
from .views import CityWeatherView

app_name = 'weather'

urlpatterns = [
    path('/<uuid:uuid>/weather', CityWeatherView.as_view(), name='city-weather'),
]
