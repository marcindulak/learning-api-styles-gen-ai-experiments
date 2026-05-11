"""URL routes for the webhooks app."""

from __future__ import annotations

from django.urls import path

from .views import github_webhook


urlpatterns = [
    path("github", github_webhook, name="github-webhook"),
]
