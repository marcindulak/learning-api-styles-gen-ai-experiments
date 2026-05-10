"""Step definitions for NFR-005: Service APIs are documented.

Adds one new assertion step:

* ``the response Content-Type starts with "..."`` — a prefix check on the
  Content-Type header. Distinct from FR-001's exact-match step
  ``the response Content-Type is "..."`` because Swagger UI's response
  carries a charset suffix (``text/html; charset=utf-8``) and the
  Gherkin asserts only the media-type prefix.

The Given and When steps used by the NFR-005 scenarios are already
defined elsewhere: ``the service is running`` (fr_007_steps),
``a client sends GET to "..."`` (fr_009_steps), ``the response status is N``
(fr_007_steps), and ``the response body contains the substring "..."``
(fr_007_steps).
"""

from __future__ import annotations

from behave import then


@then('the response Content-Type starts with "{prefix}"')
def step_response_content_type_starts_with(context, prefix: str) -> None:
    actual = context.response.get("Content-Type", "")
    assert actual.startswith(prefix), (
        f"Expected Content-Type to start with {prefix!r}, got {actual!r}."
    )
