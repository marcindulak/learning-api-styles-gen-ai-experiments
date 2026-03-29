import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="City",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("name", models.CharField(max_length=100)),
                ("country", models.CharField(max_length=100)),
                ("region", models.CharField(max_length=100)),
                ("timezone", models.CharField(max_length=50)),
                ("latitude", models.FloatField()),
                ("longitude", models.FloatField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name_plural": "cities",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="WeatherRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("city", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="weather_records", to="weather.city")),
                ("recorded_at", models.DateTimeField()),
                ("temperature_celsius", models.FloatField()),
                ("humidity_percent", models.FloatField()),
                ("wind_speed_kmh", models.FloatField()),
                ("precipitation_mm", models.FloatField(default=0.0)),
                ("description", models.CharField(blank=True, max_length=200)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-recorded_at"],
            },
        ),
        migrations.CreateModel(
            name="WeatherForecast",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("city", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="forecasts", to="weather.city")),
                ("forecast_date", models.DateField()),
                ("temperature_max_celsius", models.FloatField()),
                ("temperature_min_celsius", models.FloatField()),
                ("precipitation_mm", models.FloatField(default=0.0)),
                ("wind_speed_kmh", models.FloatField()),
                ("description", models.CharField(blank=True, max_length=200)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["forecast_date"],
                "unique_together": {("city", "forecast_date")},
            },
        ),
        migrations.CreateModel(
            name="WeatherAlert",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("city", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="alerts", to="weather.city")),
                ("severity", models.CharField(choices=[("info", "Info"), ("warning", "Warning"), ("severe", "Severe"), ("extreme", "Extreme")], max_length=20)),
                ("title", models.CharField(max_length=200)),
                ("message", models.TextField()),
                ("issued_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("created_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="alerts", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-issued_at"],
            },
        ),
    ]
