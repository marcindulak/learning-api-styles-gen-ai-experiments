"""Django admin registration for the cities app."""

from __future__ import annotations

from django.contrib import admin

from .models import City


admin.site.register(City)
