"""
ASGI config for Weather Forecast Service project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.wfs.settings')

application = get_asgi_application()
