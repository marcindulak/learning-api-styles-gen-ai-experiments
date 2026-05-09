"""Step definitions for FR-004: Weather forecast Atom feed.

Adds one assertion step used by the FR-004 scenario:

* ``the response body contains exactly N "<element>" elements`` —
  counts literal substring occurrences in the response body.
  Atom 1.0's ``<entry>`` opening tag is emitted by Django's
  :class:`django.utils.feedgenerator.Atom1Feed` with no attributes,
  so a substring count is equivalent to an element count for the
  FR-004 assertion.

The other steps used by the FR-004 scenarios (``the service is
running``, ``a city named "..." exists``, ``a client sends GET
to "..."``, ``the response status is N``, ``the response Content-Type
is "..."``, ``the response body contains the substring "..."``) are
already defined in fr_007_steps.py, fr_011_steps.py, fr_009_steps.py,
and fr_001_steps.py.
"""

from __future__ import annotations

from behave import then


@then('the response body contains exactly {count:d} "{substring}" elements')
def step_response_body_count_elements(
    context, count: int, substring: str
) -> None:
    body = context.response.content.decode("utf-8", errors="replace")
    actual = body.count(substring)
    assert actual == count, (
        f"Expected exactly {count} occurrences of {substring!r}, "
        f"found {actual}; first 500 chars were: {body[:500]!r}"
    )
