"""
URL Configuration for GraphQL API.
"""
from django.urls import path
from .views import GraphQLView

app_name = 'graphql_api'

urlpatterns = [
    path('', GraphQLView.as_view(), name='graphql'),
]
