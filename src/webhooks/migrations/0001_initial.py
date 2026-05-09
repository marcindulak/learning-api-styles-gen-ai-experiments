"""Initial schema for the webhooks app."""

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    """Creates the ``webhooks_webhookevent`` table."""

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="WebhookEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("provider", models.CharField(max_length=32)),
                ("event_type", models.CharField(max_length=64)),
                ("delivery_id", models.CharField(blank=True, max_length=128)),
                ("payload", models.JSONField()),
                ("received_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ("-received_at",),
            },
        ),
    ]
