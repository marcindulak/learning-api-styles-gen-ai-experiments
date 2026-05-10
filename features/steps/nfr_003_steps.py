"""Step definitions for NFR-003: Service is deployed as one unit.

Two scenarios share a single ``When the operator runs "..."`` step that
dispatches by command prefix:

* ``docker compose config --services`` — answered by parsing
  ``compose.yaml`` with PyYAML and emitting the service names one per
  line. PyYAML is already on the Python path as a transitive dependency
  of ``drf-spectacular``; no entry is added to ``requirements.txt``.
  Running the real ``docker`` binary is not possible from inside the
  application container (no docker CLI, no socket mount), and the
  invariant under test ("the compose configuration declares exactly one
  application service") is a property of ``compose.yaml`` itself, so
  parsing the file directly verifies the same property the docker CLI
  would report.

* ``docker compose exec app <inner>`` — answered by running ``<inner>``
  as a subprocess inside this container with ``cwd=/app``. The step is
  already executing inside the application service, so the prefix
  collapses to a same-container subprocess. ``shlex.split`` parses the
  inner command so the step does not need a real shell.

The Given step ``the file "compose.yaml" exists at the project root``
is reused from ``nfr_006_steps.py``. The Given ``the service is running``
is reused from ``fr_007_steps.py``.
"""

from __future__ import annotations

import os
import pathlib
import shlex
import subprocess
import sys

import yaml
from behave import then, when


# Subprocesses inherit this container's environment so Django settings,
# database credentials, and PYTHONPATH match the running service.
_SRC_DIR = pathlib.Path("/app")

# When the dispatcher runs a nested test runner (``manage.py behave`` or
# ``manage.py test``), the inner process tries to create the same test
# database the outer behave-django run already holds open
# (``test_${POSTGRES_DB}``). Postgres rejects the duplicate with
# "database is being accessed by other users". The fix is to point the
# nested invocation at a different production database name so its derived
# test database name does not collide. The nested DB is created and
# destroyed by the inner Django test machinery; we never write to it from
# the outer process.
_NESTED_DB_SUFFIX = "_nested"

# The inner ``manage.py behave`` would itself execute NFR-004 again and
# spawn yet another nested behave process, ad infinitum. Excluding the
# NFR-004 feature file from the inner invocation breaks the recursion
# while still verifying behave-django can run the rest of the suite.
_NESTED_BEHAVE_EXCLUDE = "NFR-004"


def _parse_compose_services(compose_path: pathlib.Path) -> list[str]:
    """Return the service names declared at the top level of ``compose.yaml``.

    Equivalent to the output of ``docker compose config --services`` for a
    well-formed compose file. Raises ``AssertionError`` (rather than a
    PyYAML / KeyError) so the failing step prints a readable reason.
    """

    document = yaml.safe_load(compose_path.read_text(encoding="utf-8"))
    assert isinstance(document, dict), (
        f"Expected {compose_path} to parse as a YAML mapping, "
        f"got {type(document).__name__}."
    )
    services = document.get("services")
    assert isinstance(services, dict), (
        f"Expected {compose_path} to declare a top-level 'services' mapping, "
        f"got {type(services).__name__}."
    )
    return list(services.keys())


def _is_django_test_runner(argv: list[str]) -> bool:
    """Return True if ``argv`` invokes a test runner that creates a test DB.

    Both ``manage.py behave`` and ``manage.py test`` ask Django to set up a
    fresh test database derived from ``DATABASES["default"]["NAME"]`` (with
    a ``test_`` prefix). When such a command is dispatched from inside an
    outer behave-django run, the inner process collides with the outer's
    open test database.
    """

    if "manage.py" not in argv:
        return False
    return "behave" in argv or "test" in argv


def _prepare_nested_runner_env(
    argv: list[str],
) -> tuple[dict[str, str], list[str]]:
    """Avoid test-DB collisions and infinite behave recursion in subprocess.

    Returns the environment to hand to ``subprocess.run`` and the (possibly
    rewritten) argv. For non-test-runner commands the parent environment
    and the argv are returned unchanged.
    """

    env = os.environ.copy()
    if not _is_django_test_runner(argv):
        return env, argv

    # Pointing the nested run at a different production DB makes its derived
    # ``test_<name>`` distinct from the outer's. The postgres user used by
    # this image has CREATEDB so the inner can create and drop its own DB.
    parent_db = env.get("POSTGRES_DB", "")
    env["POSTGRES_DB"] = parent_db + _NESTED_DB_SUFFIX

    new_argv = list(argv)
    if "behave" in new_argv:
        new_argv.append(f"--exclude={_NESTED_BEHAVE_EXCLUDE}")
    return env, new_argv


@when('the operator runs "{command}"')
def step_operator_runs(context, command: str) -> None:
    if command == "docker compose config --services":
        compose_path = context.project_root / "compose.yaml"
        services = _parse_compose_services(compose_path)
        context.command_stdout = "\n".join(services) + "\n"
        context.command_returncode = 0
        return

    prefix = "docker compose exec app "
    if command.startswith(prefix):
        inner = shlex.split(command[len(prefix) :])
        # ``python`` resolves to the same interpreter that runs behave; using
        # ``sys.executable`` makes the step robust to an unusual PATH.
        if inner and inner[0] == "python":
            inner[0] = sys.executable
        env, inner = _prepare_nested_runner_env(inner)
        completed = subprocess.run(
            inner,
            cwd=str(_SRC_DIR),
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
        context.command_stdout = completed.stdout
        context.command_returncode = completed.returncode
        return

    raise AssertionError(
        f"NFR-003 step has no handler for command: {command!r}. "
        "Add a dispatch branch in features/steps/nfr_003_steps.py if a new "
        "scenario needs one."
    )


@then('the command output contains a line "{expected}"')
def step_output_contains_line(context, expected: str) -> None:
    lines = context.command_stdout.splitlines()
    assert expected in lines, (
        f"Expected a line equal to {expected!r} in command output; got "
        f"{lines!r}."
    )


@then('the command output contains exactly one line that matches '
      'the application service "{name}"')
def step_output_contains_exactly_one_app_service(context, name: str) -> None:
    lines = context.command_stdout.splitlines()
    matches = [line for line in lines if line == name]
    assert len(matches) == 1, (
        f"Expected exactly one line equal to {name!r}; found "
        f"{len(matches)} in {lines!r}."
    )


@then('the command exits with status {code:d}')
def step_command_exit_status(context, code: int) -> None:
    actual = context.command_returncode
    assert actual == code, (
        f"Expected exit status {code}, got {actual}. "
        f"Command stdout was: {context.command_stdout!r}"
    )
