from django.db import models


class GitHubWebhookEvent(models.Model):
    event_type = models.CharField(max_length=100)
    delivery_id = models.CharField(max_length=100, unique=True)
    payload = models.JSONField()
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.event_type} ({self.delivery_id})"
