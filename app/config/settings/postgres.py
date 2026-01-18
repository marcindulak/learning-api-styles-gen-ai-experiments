"""
PostgreSQL-specific Django settings.
Used in production and Docker Compose.
"""
import os
from .base import *

# PostgreSQL Configuration (as referenced in compose.yaml)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'weather_forecast_service'),
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}

# Security
SECURE_SSL_REDIRECT = os.environ.get('TLS_ENABLE', '0') == '1'
SESSION_COOKIE_SECURE = os.environ.get('TLS_ENABLE', '0') == '1'
CSRF_COOKIE_SECURE = os.environ.get('TLS_ENABLE', '0') == '1'

# Webhook Secret
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', 'dev-webhook-secret')
