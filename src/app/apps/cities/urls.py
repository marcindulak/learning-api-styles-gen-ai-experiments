from django.urls import path, re_path
from .views import CityViewSet

app_name = 'cities'

# Create viewset instance
city_list = CityViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

city_detail = CityViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('', city_list, name='city-list'),
    path('/<uuid:uuid>', city_detail, name='city-detail'),
]
