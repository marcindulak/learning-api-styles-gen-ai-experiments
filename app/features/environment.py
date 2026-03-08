"""
Behave environment setup.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.postgres')

django.setup()


def before_scenario(context, scenario):
    """Clean up before each scenario."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    # Keep admin user, remove others
    User.objects.exclude(username='admin').delete()

    # Clean up City data if the table exists
    try:
        from weather.models import City
        City.objects.all().delete()
    except Exception:
        pass
