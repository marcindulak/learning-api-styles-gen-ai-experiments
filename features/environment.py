"""
Behave environment configuration for Weather Forecast Service tests.
"""
import os
import django

# Setup Django before importing models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from weather.models import City


def before_scenario(context, scenario):
    """Clean up test data before each scenario."""
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
