"""
WSGI config for Weather Forecast Service project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.wfs.settings')

application = get_wsgi_application()
