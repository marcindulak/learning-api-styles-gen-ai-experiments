"""Settings overlay used by the Compose-based deployment.

Inherits every default from :mod:`config.settings` and overrides only the
``DATABASES`` configuration to use the PostgreSQL service declared in
``compose.yaml``. Activated via ``DJANGO_SETTINGS_MODULE=config.postgres``
inside the application container.
"""

from __future__ import annotations

import os

from .settings import *  # noqa: F401,F403


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ["POSTGRES_HOST"],
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}
