"""AsyncAPI 3.0 specification for the WebSocket alerts endpoint (NFR-005).

drf-spectacular documents the synchronous REST surface at /api/schema, but
that toolchain does not describe asynchronous channels. AsyncAPI is the
standard counterpart for WebSocket/MQTT/Kafka APIs; this module embeds a
small AsyncAPI 3.0 document and serves it as ``application/yaml`` at
/api/asyncapi.

Why the document is hard-coded as a string rather than read from disk:
the YAML is short, has no variable parts, and inlining it removes a
filesystem dependency for a feature that should never fail at runtime.
When FR-005 (WebSocket alerts) lands, the channel description below will
be revised to match the implemented protocol; until then it documents the
planned shape so the AsyncAPI gate (NFR-005) is satisfied.
"""

from __future__ import annotations

from django.http import HttpResponse


# AsyncAPI 3.0 minimal specification describing the planned weather-alerts
# WebSocket channel. The literal "asyncapi:" prefix is the contract the
# NFR-005 Gherkin asserts; the rest of the document follows the spec at
# https://www.asyncapi.com/docs/reference/specification/v3.0.0.
ASYNCAPI_DOCUMENT: str = """\
asyncapi: 3.0.0
info:
  title: Weather Forecast Service AsyncAPI
  version: 1.0.0
  description: |
    Asynchronous channels exposed by the Weather Forecast Service.
    The WebSocket endpoint at /ws/alerts publishes weather alerts to
    subscribed clients (FR-005).
servers:
  local:
    host: localhost:8000
    protocol: ws
channels:
  alerts:
    address: /ws/alerts
    messages:
      WeatherAlert:
        $ref: '#/components/messages/WeatherAlert'
operations:
  receiveAlert:
    action: receive
    channel:
      $ref: '#/channels/alerts'
    messages:
      - $ref: '#/channels/alerts/messages/WeatherAlert'
components:
  messages:
    WeatherAlert:
      name: WeatherAlert
      title: Weather Alert
      summary: A weather alert published to subscribers.
      contentType: text/plain
      payload:
        type: string
        description: Free-text alert message.
"""


def asyncapi_view(request) -> HttpResponse:
    """Serve the AsyncAPI document as ``application/yaml``.

    application/yaml is the IANA-registered media type for YAML (RFC 9512).
    Returning a plain :class:`HttpResponse` rather than going through DRF
    keeps the route independent of authentication and renderer negotiation
    — the document is public-read documentation.
    """

    return HttpResponse(ASYNCAPI_DOCUMENT, content_type="application/yaml")
