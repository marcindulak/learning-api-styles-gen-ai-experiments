from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CityViewSet

app_name = 'cities'

router = DefaultRouter(trailing_slash=False)
router.register(r'', CityViewSet, basename='city')

urlpatterns = [
    path('', include(router.urls)),
]
