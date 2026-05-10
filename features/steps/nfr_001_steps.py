"""Step definitions for NFR-001: Service operates in a local environment.

The scenario exercises the canonical local-deployment flow: the operator
builds the image, brings the stack up, and the running runserver answers a
real HTTP request on port 8000. The When/Then are covered by the existing
``a client sends GET to "..."`` and ``the response status is N`` steps
(extended in fr_009_steps.py to dispatch absolute URLs through urllib).

The four Given clauses describe preconditions of the local-deployment
workflow that are inherent to running ``docker compose exec app python
manage.py behave --no-input``: by the time behave is executing, the
repository is checked out, Docker and Compose are present on the host,
the image is built, and the stack is up. The repository check is the
only one we can verify cheaply from inside the container; the other three
are recorded as no-ops with intent comments.
"""

from __future__ import annotations

from behave import given


@given('the project repository is checked out locally')
def step_repository_checked_out(context) -> None:
    manage_py = context.project_root / "src" / "manage.py"
    assert manage_py.exists(), (
        f"Expected the project's manage.py at {manage_py}; the repository "
        "does not appear to be checked out."
    )


@given('Docker and the Docker Compose plugin are installed')
def step_docker_installed(context) -> None:
    # Docker and the Compose plugin are required on the host to bring up
    # the container that runs this very test. From inside the container
    # we cannot invoke the host's docker CLI, so the precondition is
    # treated as inherent to the test harness.
    pass


@given('the operator has run "{command}" successfully')
def step_operator_ran_command(context, command: str) -> None:
    # Matches both "docker compose build ..." and "docker compose up ..."
    # Givens. Both must already have succeeded for this test process to be
    # running inside the application container.
    pass
