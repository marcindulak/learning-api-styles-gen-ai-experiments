from behave import given, then, when
from django.db import connection

from nfr_004_testability_steps import _run

# Mirrors the "genuinely true by construction" pattern established in
# nfr_004_testability_steps.py: these steps run via `docker compose exec app
# python manage.py behave`, so the "docker compose up --detach --wait"
# precondition they describe has already happened by the time behave starts.
# The Then steps below still perform a real check rather than trusting that
# construction blindly.


@given("the repository is checked out locally")
def step_given_repository_checked_out(context):
    pass


@when('the operator runs "docker compose up --detach --wait"')
def step_when_operator_runs_compose_up(context):
    pass


@given('the service was started with "docker compose up --detach --wait"')
def step_given_service_started(context):
    pass


@then('the "{service}" container reports a healthy status')
def step_then_container_healthy(context, service):
    if service == "app":
        # Reuses the Dockerfile's own HEALTHCHECK script (see NFR-004) rather
        # than a docker socket mount + `docker inspect`: that would need
        # root-equivalent host access just to observe a fact this container
        # can already prove about itself over HTTP.
        result = _run(["bash", "scripts/healthcheck.sh"])
        assert result.returncode == 0, f"app healthcheck failed:\n{result.stdout}{result.stderr}"
    elif service == "db":
        # A real psycopg connection via the ORM's own configured database,
        # not a mock: proves the same fact postgres's own `pg_isready`
        # healthcheck does, without adding a new client dependency.
        connection.ensure_connection()
        assert connection.is_usable(), "db connection is not usable"
    else:
        raise ValueError(f"no health check defined for service {service!r}")
