"""Step definitions for NFR-006: project is runnable by majority of book readers.

The scenarios assert filesystem-level facts about the repository (Dockerfile,
compose.yaml, devcontainer.json), so the steps perform direct path and content
checks against ``context.project_root`` (set in features/environment.py).
"""

from __future__ import annotations

import pathlib

from behave import given, then, when


@given('the project repository is checked out')
def step_repo_checked_out(context) -> None:
    project_root: pathlib.Path = context.project_root
    assert project_root.is_dir(), f"Project root not found: {project_root}"


@when('the operator inspects the repository')
def step_inspect_repository(context) -> None:
    # Inspection itself happens in the following Then steps, which read paths
    # under context.project_root. This step exists to keep the Gherkin readable.
    pass


# behave matches steps by ``(keyword, text)``: a Then-only registration would
# leave NFR-003's ``Given the file "compose.yaml" exists at the project root``
# undefined. Registering both keywords on one body keeps the assertion in one
# place rather than duplicating it into a sibling step file.
@given('the file "{relative_path}" exists at the project root')
@then('the file "{relative_path}" exists')
@then('the file "{relative_path}" exists at the project root')
def step_file_exists(context, relative_path: str) -> None:
    target = context.project_root / relative_path
    assert target.is_file(), f"Expected file to exist: {target}"


@then('"{relative_path}" references the project\'s "{referenced_name}"')
def step_file_references(context, relative_path: str, referenced_name: str) -> None:
    target = context.project_root / relative_path
    assert target.is_file(), f"Expected file to exist: {target}"
    content = target.read_text(encoding="utf-8")
    assert referenced_name in content, (
        f"Expected {target} to reference {referenced_name!r}, "
        f"but the substring was not found in its content."
    )
