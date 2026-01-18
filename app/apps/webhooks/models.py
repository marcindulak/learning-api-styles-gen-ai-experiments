from django.db import models
import json


class GitHubWebhook(models.Model):
    """
    Model to store GitHub webhook events.
    """
    event_type = models.CharField(max_length=50, db_index=True)
    payload = models.JSONField()
    signature = models.CharField(max_length=255, blank=True, null=True)
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.event_type} - {self.created_at}"
