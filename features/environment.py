"""Behave environment hooks shared by all feature suites.

Two responsibilities:

1. Expose ``context.project_root`` so filesystem-only steps (e.g. NFR-006) can
   reference paths relative to the repository.

2. Make every Django-backed scenario start with a clean database. Each
   scenario runs inside a transaction that is rolled back in
   ``after_scenario``, so users/sessions created by one scenario do not leak
   into the next.

The hooks support both invocation paths used in this project:

* ``python manage.py behave --no-input`` (the canonical command from
  REQUIREMENTS.md). behave-django configures Django and creates the test
  database before our hooks run.

* Plain ``behave`` (used while bootstrapping the project, e.g. when only
  filesystem-level features such as NFR-006 are being verified). In that
  mode we configure Django ourselves if and only if ``src/`` and the
  ``django`` package are both available; otherwise we run as a pure
  filesystem suite.
"""

from __future__ import annotations

import os
import pathlib
import sys


def _bootstrap_django(context) -> bool:
    """Make Django usable to step definitions. Returns True if Django is ready.

    Two invocation paths converge here:

    * ``python manage.py behave`` — behave-django has already imported the
      Django app registry and created the test database. We detect this by
      checking ``django.apps.apps.ready`` and simply mark that we do not own
      the test DB lifecycle.

    * Plain ``behave`` (no manage.py) — Django has not been configured yet.
      We add ``src/`` to ``sys.path``, set ``DJANGO_SETTINGS_MODULE``, call
      ``django.setup()`` and create a test database ourselves. If Django is
      not installed (e.g. the bare environment used to run NFR-006 only),
      this returns False and the suite continues with filesystem-only steps.
    """

    try:
        from django.apps import apps
    except ModuleNotFoundError:
        return False

    if apps.ready:
        context.django_owns_db = False
        return True

    src_path = context.project_root / "src"
    if not src_path.is_dir():
        return False

    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    import django

    django.setup()
    from django.test.runner import DiscoverRunner
    from django.test.utils import setup_test_environment

    setup_test_environment()
    runner = DiscoverRunner(verbosity=0, interactive=False)
    context.django_test_runner = runner
    context.django_old_db_config = runner.setup_databases()
    context.django_owns_db = True
    return True


def before_all(context) -> None:
    # When the suite runs inside the application container, the host's
    # repository is not at ``../`` from this file — it is bind-mounted via
    # the ``PROJECT_ROOT`` environment variable. Filesystem-only steps
    # (NFR-006) inspect Dockerfile/compose.yaml which only exist at that
    # path. Outside the container we fall back to the repo-relative path.
    project_root_env = os.environ.get("PROJECT_ROOT")
    if project_root_env and pathlib.Path(project_root_env).is_dir():
        context.project_root = pathlib.Path(project_root_env)
    else:
        # features/environment.py -> features/ -> project root
        context.project_root = pathlib.Path(__file__).resolve().parent.parent
    context.django_ready = _bootstrap_django(context)


def before_scenario(context, scenario) -> None:
    """Wrap each scenario in a transaction that is rolled back afterwards.

    Skipped when Django is not bootstrapped, so filesystem-only suites such
    as NFR-006 still run when the Django stack is unavailable.
    """

    if not getattr(context, "django_ready", False):
        return

    from django.db import transaction
    from django.test import Client

    context.atomic = transaction.atomic(using="default")
    context.atomic.__enter__()
    context.client = Client()


def after_scenario(context, scenario) -> None:
    if not getattr(context, "django_ready", False):
        return
    if not hasattr(context, "atomic"):
        return

    from django.db import transaction

    transaction.set_rollback(True)
    context.atomic.__exit__(None, None, None)
    del context.atomic


def after_all(context) -> None:
    if not getattr(context, "django_ready", False):
        return
    if not getattr(context, "django_owns_db", False):
        return

    from django.test.utils import teardown_test_environment

    context.django_test_runner.teardown_databases(context.django_old_db_config)
    teardown_test_environment()
