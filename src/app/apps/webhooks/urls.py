from django.urls import path
from .views import GitHubWebhookView, WebhookEventListView

app_name = 'webhooks'

urlpatterns = [
    path('', GitHubWebhookView.as_view(), name='github-webhook'),
    path('/events', WebhookEventListView.as_view(), name='webhook-events'),
]
