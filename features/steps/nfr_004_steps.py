"""Step definitions for NFR-004: Service is testable.

NFR-004's two scenarios assert that ``manage.py behave`` and
``manage.py test`` exit 0 when run inside the application container. The
``When the operator runs "..."`` step and its ``Then the command exits
with status N`` companion are reused from ``nfr_003_steps.py``: that
file's dispatcher already handles ``docker compose exec app <inner>`` by
running ``<inner>`` as a subprocess in the container, and it adds the
collision-avoidance flags when the inner command is a Django test
runner (a different ``POSTGRES_DB`` for the test DB, plus
``--exclude=NFR-004`` for nested behave runs).

The Given step ``the service container is running`` is unique to NFR-004
and is defined here. It verifies the container's source tree (``/app``)
and the project root (mounted at ``/workspace`` per ``compose.yaml``) are
both reachable, so a misconfigured stack fails at the precondition with a
readable message rather than later inside the subprocess.
"""

from __future__ import annotations

import pathlib

from behave import given


@given('the service container is running')
def step_service_container_running(context) -> None:
    src_dir = pathlib.Path("/app")
    assert src_dir.is_dir(), (
        f"Expected the application source tree at {src_dir}; this step "
        "must run inside the application container as configured by "
        "compose.yaml's volume mount './src:/app'."
    )
    manage_py = src_dir / "manage.py"
    assert manage_py.is_file(), (
        f"Expected {manage_py} to exist; without manage.py the "
        "operator cannot invoke the Django test runners NFR-004 asserts."
    )
    assert pathlib.Path(context.project_root).is_dir(), (
        f"Expected project root {context.project_root} to be a directory; "
        "compose.yaml mounts the host repository at /workspace and "
        "before_all sets context.project_root to that path."
    )
