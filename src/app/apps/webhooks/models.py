import uuid
from django.db import models


class WebhookEvent(models.Model):
    """
    Model representing a GitHub webhook event received by the service.
    """
    EVENT_TYPES = [
        ('push', 'Push'),
        ('pull_request', 'Pull Request'),
        ('issues', 'Issues'),
        ('issue_comment', 'Issue Comment'),
        ('create', 'Create'),
        ('delete', 'Delete'),
        ('fork', 'Fork'),
        ('star', 'Star'),
        ('release', 'Release'),
        ('other', 'Other'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    delivery_id = models.CharField(max_length=255, unique=True)
    payload = models.JSONField()
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-received_at']
        indexes = [
            models.Index(fields=['event_type']),
            models.Index(fields=['delivery_id']),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.delivery_id}"
