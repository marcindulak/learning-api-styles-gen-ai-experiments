import os
import subprocess

from behave import given, then, when
from django.conf import settings

# Real, separate "python manage.py behave" invocations (not a mock of the
# command's behavior) targeting the probe fixture directory below, which
# lives outside features/ so the project's normal, path-less
# "python manage.py behave --no-input" run never discovers or runs it.
# --use-existing-database avoids the nested process dropping/recreating the
# test database this very scenario is already running inside of.
PROBE_FEATURES_DIR = "tests/fixtures/behave_probe/features"
E2E_SCRIPT = "tests/e2e.sh"

_PROBE_TAG_FOR_OUTCOME = {"passing": "nfr_004_probe_pass", "failing": "nfr_004_probe_fail"}

# The passing/failing cases each run as a separate Scenario Outline example
# (one subprocess per When), not concurrently: an earlier draft ran both
# under a single When step to save wall time, but that fused two independent
# stimuli into one step, which the /simplify altitude review flagged as the
# wrong Gherkin shape for what this scenario is actually asserting. Kept as
# two examples (correctness/clarity) over re-introducing that fusion for a
# speed gain in a test-only code path.


def _run(command, **kwargs):
    return subprocess.run(command, cwd=settings.BASE_DIR, capture_output=True, text=True, **kwargs)


def _run_probe(outcome):
    tag = _PROBE_TAG_FOR_OUTCOME[outcome]
    return _run(["python", "manage.py", "behave", "--no-input", "--use-existing-database", PROBE_FEATURES_DIR, f"--tags=@{tag}"])


def _run_e2e(outcome):
    # An address nothing listens on forces curl's own connection failure,
    # exercising the script's real non-zero exit path rather than asserting
    # it abstractly.
    port = os.environ.get("APP_PORT_HTTP", "8000")
    base_url = f"http://localhost:{port}" if outcome == "passing" else "http://localhost:1"
    return _run(["bash", E2E_SCRIPT], env={**os.environ, "E2E_BASE_URL": base_url})


@given("the project's integration test command is available")
def step_given_integration_command_available(context):
    result = _run(["python", "manage.py", "behave", "--help"])
    assert result.returncode == 0, f"python manage.py behave --help did not succeed:\n{result.stdout}{result.stderr}"


@when("the operator runs a {outcome} integration test suite")
def step_when_runs_integration_suite(context, outcome):
    context.last_process = _run_probe(outcome)
    context.last_exit_code = context.last_process.returncode


@given('the service is running via "docker compose up --detach --wait"')
def step_given_service_running(context):
    # Genuinely true by construction: this very step runs inside behave,
    # itself invoked via `docker compose exec app ...` against the same
    # `app` container `docker compose up --detach --wait` already started
    # and health-checked. Reuses the Dockerfile's own HEALTHCHECK script
    # rather than reimplementing its "what counts as healthy" logic here.
    result = _run(["bash", "scripts/healthcheck.sh"])
    assert result.returncode == 0, f"scripts/healthcheck.sh reported the service unhealthy:\n{result.stdout}{result.stderr}"


@when("the operator runs a {outcome} end-to-end test suite against the running service")
def step_when_runs_e2e_suite(context, outcome):
    context.last_process = _run_e2e(outcome)
    context.last_exit_code = context.last_process.returncode


@then("the command's exit status reflects that the suite is {outcome}")
def step_then_exit_status_reflects_outcome(context, outcome):
    diagnostic = f"exit={context.last_exit_code}\n{context.last_process.stdout}{context.last_process.stderr}"
    if outcome == "passing":
        assert context.last_exit_code == 0, diagnostic
    else:
        assert context.last_exit_code != 0, diagnostic
