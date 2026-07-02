"""Steps that verify the service is runnable by book readers.

The suite executes inside the "django-app" container, which only exists
because the documented "docker compose build" and "docker compose up"
commands were executed on the host. The build command is therefore
verified through its observable effects: the running interpreter and
filesystem match what the project Dockerfile produces, and the container
user matches the UID the build arguments were derived from. Repository
root files (README.md, .devcontainer/, compose.yaml, Dockerfile) are
read through their read-only mounts under /app.
"""
import json
import os
import re
import sys

import parse
from behave import given, register_type, then, when

REPO_ROOT = "/app"


@parse.with_pattern(r'[^"]*')
def parse_quoted(text):
    return text


register_type(Q=parse_quoted)


@given(
    'the stack was built with "docker compose build '
    '--build-arg UID=$(id -u) --build-arg GID=$(id -g)"'
)
def step_stack_was_built(context):
    # The running container proves the build: its interpreter version must
    # match the Dockerfile's PY_VER (the Dockerfile asserts this at build
    # time), and the TLS directories the Dockerfile creates must exist.
    with open(os.path.join(REPO_ROOT, "Dockerfile")) as dockerfile:
        match = re.search(r"^ARG PY_VER=(\S+)", dockerfile.read(), re.MULTILINE)
    assert match, "Dockerfile does not define the PY_VER build argument"
    running = f"{sys.version_info[0]}.{sys.version_info[1]}"
    assert running == match.group(1), (
        f"running Python {running}, but the Dockerfile builds {match.group(1)}"
    )
    for env_var in ("APP_TLS_CERTS_DIR", "APP_TLS_PRICATE_DIR"):
        directory = os.environ.get(env_var, "")
        assert os.path.isdir(directory), (
            f"directory {env_var}={directory} from the Dockerfile is missing"
        )
    # The UID/GID build arguments make the container user own the
    # bind-mounted checkout, exactly like the invoking host user does.
    owner = os.stat(os.path.join(REPO_ROOT, "manage.py")).st_uid
    assert os.getuid() == owner, (
        f"container user uid {os.getuid()} does not own the mounted "
        f"repository files (owner uid {owner}); the UID build argument "
        f"did not take effect"
    )


@given("a checkout of the repository")
def step_checkout_of_the_repository(context):
    for marker in ("compose.yaml", "Dockerfile", "manage.py"):
        path = os.path.join(REPO_ROOT, marker)
        assert os.path.isfile(path), f"repository file {path} is missing"


@when('the file "{path:Q}" is read')
def step_read_repository_file(context, path):
    with open(os.path.join(REPO_ROOT, path)) as repository_file:
        context.file_text = repository_file.read()


@then('it contains the command "{command:Q}"')
def step_file_contains_command(context, command):
    assert command in context.file_text, (
        f'the file does not contain the command "{command}"'
    )


def json_document(context):
    try:
        return json.loads(context.file_text)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"the file is not valid JSON: {exc}")


@then("it is a valid JSON document")
def step_file_is_valid_json(context):
    json_document(context)


@then('it references the "{name:Q}" file')
def step_devcontainer_references_file(context, name):
    compose_files = json_document(context).get("dockerComposeFile", [])
    if isinstance(compose_files, str):
        compose_files = [compose_files]
    referenced = [os.path.basename(entry) for entry in compose_files]
    assert name in referenced, (
        f'"dockerComposeFile" references {referenced}, not "{name}"'
    )


@then('it sets the service to "{name:Q}"')
def step_devcontainer_sets_service(context, name):
    service = json_document(context).get("service")
    assert service == name, f'"service" is "{service}", expected "{name}"'
