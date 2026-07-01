"""ASGI config for the Weather Forecast Service."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.postgres")

application = get_asgi_application()
