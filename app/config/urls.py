"""
URL Configuration for Weather Forecast Service.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

# Health check endpoint
def health_check(request):
    return JsonResponse({'status': 'healthy'})

urlpatterns = [
    # Health check
    path('health/', health_check, name='health_check'),

    # Admin
    path('admin/', admin.site.urls),

    # API
    path('api/', include('apps.api.urls')),
]
