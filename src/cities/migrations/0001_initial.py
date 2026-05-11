"""Initial schema for the cities app."""

from __future__ import annotations

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    """Creates the ``cities_city`` table."""

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="City",
            fields=[
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                ("country", models.CharField(max_length=100)),
                ("region", models.CharField(max_length=100)),
                ("timezone", models.CharField(max_length=64)),
                ("latitude", models.DecimalField(decimal_places=6, max_digits=9)),
                ("longitude", models.DecimalField(decimal_places=6, max_digits=9)),
            ],
            options={
                "ordering": ("name",),
                "verbose_name_plural": "cities",
            },
        ),
    ]
