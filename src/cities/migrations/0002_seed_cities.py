"""Seeds the five supported cities (FR-009)."""

from __future__ import annotations

from django.db import migrations

from cities.seed import SEED_CITIES, seed_cities


def forwards(apps, schema_editor):
    seed_cities(apps.get_model("cities", "City"))


def backwards(apps, schema_editor):
    City = apps.get_model("cities", "City")
    City.objects.filter(name__in=[row[0] for row in SEED_CITIES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("cities", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=backwards),
    ]
