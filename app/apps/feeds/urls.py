from django.urls import path
from . import views

urlpatterns = [
    path('atom/', views.AtomFeedView.as_view(), name='atom-feed'),
]
