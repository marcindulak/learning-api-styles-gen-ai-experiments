from django.urls import path
from .views import WeatherAtomFeedView

app_name = 'feeds'

urlpatterns = [
    path('<uuid:city_uuid>/feed.atom', WeatherAtomFeedView.as_view(), name='city-feed'),
]
