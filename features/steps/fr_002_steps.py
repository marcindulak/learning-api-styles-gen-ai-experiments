"""Step definitions for FR-002: GraphQL API exposes common weather indicators.

Adds one new step used by the FR-002 scenarios:

* ``a client sends a GraphQL query "..." to "..."`` — POSTs the named
  GraphQL query as JSON to the named URL and stores the response on the
  behave context.

The step uses behave's regex matcher (``use_step_matcher("re")``) rather
than the default parse matcher because the FR-002 Gherkin embeds
backslash-escaped double quotes inside the query argument
(``... currentWeather(city: \\"Tokyo\\") ...``). Parse's
``"{name}"`` placeholder uses non-greedy ``.+?`` between literal quotes
and would terminate the capture at the first inner ``"`` instead of at
the trailing delimiter. A regex with a greedy capture and a tail-anchored
URL group resolves the query unambiguously, and the captured ``\\"`` are
unescaped to ``"`` before the query is sent so the server receives a
syntactically valid GraphQL document.

Reused steps:

* ``the service is running`` (FR-007).
* ``a city named "..." exists`` (FR-011).
* ``the response status is N`` (FR-007).
* ``the response body has a key "..." with a numeric value``
  (FR-001, generalised to support dotted paths).
* ``the response body has a key "..." with the value "..."`` (FR-006).
"""

from __future__ import annotations

import json

from behave import use_step_matcher, when

# Switch this file to regex matching for the only step it defines. behave
# scopes the matcher choice per-decorator at registration time, so files
# loaded after this one are not affected.
use_step_matcher("re")


@when(
    r'a client sends a GraphQL query "(?P<query>.+)" to "(?P<url>[^"]+)"'
)
def step_send_graphql_query(context, query: str, url: str) -> None:
    # The Gherkin source uses \" to embed a literal double-quote inside the
    # captured query string; restore the unescaped form before forwarding to
    # the server. Backslash-escaping any other character is not part of the
    # FR-002 contract, so only \" is unescaped here.
    payload = {"query": query.replace('\\"', '"')}
    context.response = context.client.post(
        url,
        data=json.dumps(payload),
        content_type="application/json",
    )
    # Force the response body to be re-parsed by the JSON helpers in
    # fr_001_steps / fr_006_steps; without this, an earlier scenario's
    # cached value would mask the new response.
    context.response_json = None


# Restore parse matching so any later-loaded files (alphabetically after
# fr_002_steps.py) keep the project default.
use_step_matcher("parse")
