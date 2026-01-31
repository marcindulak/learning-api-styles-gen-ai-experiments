from django.urls import path, include

app_name = 'api'

urlpatterns = [
    # Authentication
    path('', include('apps.authentication.urls')),

    # Cities
    path('cities', include('apps.cities.urls')),
]
