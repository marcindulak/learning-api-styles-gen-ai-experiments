"""Database models for the webhooks app.

A :class:`WebhookEvent` row records one incoming webhook delivery whose
HMAC signature has been verified. Rejected (unsigned or wrong-signature)
deliveries are intentionally not persisted; FR-003's "the event is not
recorded in the webhook log" assertion relies on that absence.
"""

from __future__ import annotations

from django.db import models


class WebhookEvent(models.Model):
    """One verified webhook delivery from an external provider.

    The provider is stored explicitly (rather than implied by the URL)
    so a future iteration can add Stripe/Slack/Bitbucket endpoints
    without splitting the log into per-provider tables.
    """

    provider = models.CharField(max_length=32)
    event_type = models.CharField(max_length=64)
    delivery_id = models.CharField(max_length=128, blank=True)
    payload = models.JSONField()
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-received_at",)

    def __str__(self) -> str:
        return f"{self.provider}:{self.event_type} at {self.received_at.isoformat()}"
