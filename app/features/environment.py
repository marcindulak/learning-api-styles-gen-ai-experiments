"""
Behave environment configuration for Weather Forecast Service tests.
"""
import json
import os
import subprocess
import django

# Setup Django before importing models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from weather.models import City, CurrentWeather, WeatherForecast, WeatherAlert, WebhookEvent


def before_scenario(context, scenario):
    """Clean up test data before each scenario."""
    try:
        CurrentWeather.objects.all().delete()
    except Exception:
        # Table might not exist yet
        pass

    try:
        WeatherForecast.objects.all().delete()
    except Exception:
        # Table might not exist yet
        pass

    try:
        WeatherAlert.objects.all().delete()
    except Exception:
        # Table might not exist yet
        pass

    try:
        WebhookEvent.objects.all().delete()
    except Exception:
        # Table might not exist yet
        pass

    try:
        City.objects.all().delete()
    except Exception:
        # City table might not exist yet in early feature implementations
        pass

    # Clean up non-admin users (preserve admin for testing)
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        User.objects.filter(is_superuser=False).delete()
    except Exception:
        pass

    # Clear webhook secret in Django server process for each scenario
    try:
        payload = json.dumps({"key": "GITHUB_WEBHOOK_SECRET", "value": ""})
        cmd = [
            "curl",
            "--data", payload,
            "--header", "Content-Type: application/json",
            "--request", "POST",
            "--silent",
            "http://localhost:8000/api/test/set-env/"
        ]
        subprocess.run(cmd, check=True, capture_output=True)
    except Exception:
        pass
