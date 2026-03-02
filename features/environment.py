"""Behave environment configuration."""

import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.wfs.settings')
django.setup()


def before_scenario(context, scenario):
    """Clean up the database before each scenario."""
    from src.weather.models import City, WebhookEvent
    City.objects.all().delete()
    WebhookEvent.objects.all().delete()

    import subprocess
    subprocess.run(
        [
            'curl',
            '--data', '{"GITHUB_WEBHOOK_SECRET": ""}',
            '--header', 'Content-Type: application/json',
            '--request', 'POST',
            '--silent',
            'http://localhost:8000/api/test/set-env/'
        ],
        capture_output=True,
        timeout=5
    )


def after_scenario(context, scenario):
    """Clean up after each scenario."""
    if hasattr(context, 'weather_api_test_mode'):
        import subprocess
        subprocess.run(
            [
                'curl',
                '--data', '{}',
                '--header', 'Content-Type: application/json',
                '--request', 'POST',
                '--silent',
                'http://localhost:8000/api/test/set-mode/'
            ],
            capture_output=True,
            timeout=5
        )
        delattr(context, 'weather_api_test_mode')
