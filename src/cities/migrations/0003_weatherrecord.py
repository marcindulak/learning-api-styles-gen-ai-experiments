"""Schema migration for the WeatherRecord model (FR-006)."""

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    """Creates the ``cities_weatherrecord`` table."""

    dependencies = [
        ("cities", "0002_seed_cities"),
    ]

    operations = [
        migrations.CreateModel(
            name="WeatherRecord",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("observed_on", models.DateField()),
                ("temperature", models.FloatField()),
                ("humidity", models.FloatField(blank=True, null=True)),
                ("wind_speed", models.FloatField(blank=True, null=True)),
                ("pressure", models.FloatField(blank=True, null=True)),
                (
                    "city",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="weather_records",
                        to="cities.city",
                    ),
                ),
            ],
            options={
                "ordering": ("-observed_on",),
                "unique_together": {("city", "observed_on")},
            },
        ),
    ]
