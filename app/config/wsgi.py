"""
WSGI config for Weather Forecast Service.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.postgres")

application = get_wsgi_application()
