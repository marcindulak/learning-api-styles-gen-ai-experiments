"""Step definitions for FR-001: REST API exposes common weather indicators.

Adds two assertion steps used by the FR-001 scenarios:

* ``the response Content-Type is "..."`` — exact-match check on the
  response's Content-Type header.

* ``the response body has a key "..." with a numeric value`` — verifies
  that the JSON response contains the named key and that its value is
  numeric (``int`` or ``float``, but not ``bool`` since ``bool`` is a
  subclass of ``int`` in Python and a True/False value would otherwise
  silently pass the check).

The When and Given steps used by the FR-001 scenarios are already
defined in ``fr_007_steps.py`` (``the service is running``,
``the response status is N``), ``fr_009_steps.py``
(``a client sends GET to "..."``), and ``fr_011_steps.py``
(``a city named "..." exists``).
"""

from __future__ import annotations

import json
from numbers import Real

from behave import then


def _decode_json(context):
    """Parse the latest response body as JSON, caching it on the context.

    Mirrors the helper in fr_009_steps.py but is duplicated locally so
    each feature's steps can be read in isolation (CLAUDE.md prefers
    AHA over premature DRY for cross-feature step utilities).
    """

    if not hasattr(context, "response_json") or context.response_json is None:
        context.response_json = json.loads(
            context.response.content.decode("utf-8")
        )
    return context.response_json


@then('the response Content-Type is "{content_type}"')
def step_response_content_type(context, content_type: str) -> None:
    actual = context.response.get("Content-Type", "")
    # DRF appends "; charset=utf-8" by default, so compare on the media
    # type prefix rather than the full header value.
    assert actual.split(";", 1)[0].strip() == content_type, (
        f"Expected Content-Type {content_type!r}, got {actual!r}."
    )


@then('the response body has a key "{key}" with a numeric value')
def step_response_key_numeric(context, key: str) -> None:
    body = _decode_json(context)
    assert key in body, f"Key {key!r} not found; body keys: {list(body)}"
    value = body[key]
    # Reject bool explicitly because in Python ``isinstance(True, int)``
    # is True, and a boolean weather reading would be a bug, not a pass.
    assert isinstance(value, Real) and not isinstance(value, bool), (
        f"Expected numeric value at {key!r}, got {value!r} ({type(value).__name__})."
    )
