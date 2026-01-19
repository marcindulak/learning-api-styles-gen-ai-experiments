from django.urls import path
from . import views

app_name = 'webhooks'

urlpatterns = [
    path('github/', views.github_webhook, name='github_webhook'),
]
