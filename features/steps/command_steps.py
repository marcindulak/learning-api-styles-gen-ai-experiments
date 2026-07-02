"""Steps for executing shell commands inside the app container.

behave itself runs inside the "django-app" container (see NFR-001), so
executing a command "in the app container" is a local subprocess with
cwd /app. Nested "manage.py behave" invocations receive a distinct test
database name via the POSTGRES_TEST_DB environment variable so they
cannot collide with the test database held open by the outer run.
"""
import json
import os
import re
import subprocess

import parse
from behave import register_type, then, when


@parse.with_pattern(r'[^"]*')
def parse_quoted(text):
    return text


register_type(Q=parse_quoted)

NESTED_TEST_DB = "test_{}_nested".format(
    os.environ.get("POSTGRES_DB", "weather_forecast_service")
)


@when('the command "{command:Q}" is executed in the "{container:Q}" container')
def step_execute_command_in_container(context, command, container):
    assert container == "app", (
        f'steps run inside the "app" container and cannot execute '
        f'commands in the "{container}" container'
    )
    env = dict(os.environ, POSTGRES_TEST_DB=NESTED_TEST_DB)
    context.command_result = subprocess.run(
        command,
        shell=True,
        cwd="/app",
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )


@then("the command exits with status code {expected:d}")
def step_command_exit_code(context, expected):
    result = context.command_result
    assert result.returncode == expected, (
        f"expected exit code {expected}, got {result.returncode}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )


def summary_count(context, unit, category):
    """Extract a count from behave's summary line for `unit`.

    The line looks like "0 steps passed, 0 failed, 41 skipped, 9 undefined";
    a category absent from the line means a count of zero.
    """
    result = context.command_result
    output = result.stdout + result.stderr
    line_match = re.search(rf"^\d+ {unit}s? passed.*$", output, re.MULTILINE)
    assert line_match, (
        f"no '{unit}' summary line found in command output\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    count_match = re.search(rf"(\d+) {category}", line_match.group(0))
    return int(count_match.group(1)) if count_match else 0


@then("the output reports {expected:d} undefined steps")
def step_output_undefined_steps(context, expected):
    actual = summary_count(context, "step", "undefined")
    assert actual == expected, (
        f"expected {expected} undefined steps, got {actual}\n"
        f"stdout:\n{context.command_result.stdout}"
    )


@then("the output reports {expected:d} failed scenarios")
def step_output_failed_scenarios(context, expected):
    actual = summary_count(context, "scenario", "failed")
    assert actual == expected, (
        f"expected {expected} failed scenarios, got {actual}\n"
        f"stdout:\n{context.command_result.stdout}"
    )


@then("the command output is valid JSON")
def step_command_output_is_json(context):
    result = context.command_result
    try:
        json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"command output is not valid JSON: {exc}\n"
            f"stdout:\n{result.stdout}"
        )
