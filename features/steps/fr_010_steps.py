"""Step definitions for FR-010: Forecast horizon limited to 7 days.

Adds one assertion step:

* ``the response body has a key "..." with a list of length N`` — asserts
  that the JSON response contains the named key, that its value is a
  list (not a string or dict), and that its length matches the expected
  count.

The other steps used by the FR-010 scenarios are reused from earlier
features:

* ``the service is running`` (FR-007).
* ``a city named "..." exists`` (FR-011).
* ``a client sends GET to "..."`` (FR-009).
* ``the response status is N`` (FR-007).
* ``the response body has a key "..." with a value containing "..."``
  (FR-009).
"""

from __future__ import annotations

import json

from behave import then


def _decode_json(context):
    """Parse the latest response body as JSON, caching it on the context."""

    if not hasattr(context, "response_json") or context.response_json is None:
        context.response_json = json.loads(
            context.response.content.decode("utf-8")
        )
    return context.response_json


@then('the response body has a key "{key}" with a list of length {length:d}')
def step_response_key_list_length(context, key: str, length: int) -> None:
    body = _decode_json(context)
    assert key in body, f"Key {key!r} not found; body keys: {list(body)}"
    value = body[key]
    assert isinstance(value, list), (
        f"Expected a list at {key!r}, got {type(value).__name__}: {value!r}."
    )
    assert len(value) == length, (
        f"Expected list of length {length} at {key!r}, got length {len(value)}."
    )
