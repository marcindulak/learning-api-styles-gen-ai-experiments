from django.urls import path
from .views import HistoricalViewSet

app_name = 'historical'

historical_list = HistoricalViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

urlpatterns = [
    path('/<uuid:city_uuid>/historical', historical_list, name='city-historical'),
]
