"""Behave environment configuration."""

import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.wfs.settings')
django.setup()
