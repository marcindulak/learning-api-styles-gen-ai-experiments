"""Step definitions for FR-003: GitHub webhook integration.

Reuses ``the service is running`` and ``the response status is N`` from
FR-007. Adds steps for configuring the shared HMAC secret, sending a
signed/unsigned POST to ``/webhooks/github``, and asserting that the
:class:`webhooks.models.WebhookEvent` log was (or was not) appended.

The shared secret is applied via :func:`django.test.utils.override_settings`
so the override is undone in ``after_scenario`` via the
``context.scenario_cleanups`` hook from ``features/environment.py``.
"""

from __future__ import annotations

import hashlib
import hmac
import json

from behave import given, then, when


_DEFAULT_PAYLOAD = {"zen": "Speak like a human.", "hook_id": 1, "ref": "refs/heads/main"}


def _sign(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return "sha256=" + digest


@given('the GitHub webhook secret is configured to "{secret}"')
def step_configure_webhook_secret(context, secret: str) -> None:
    from django.test.utils import override_settings

    override = override_settings(GITHUB_WEBHOOK_SECRET=secret)
    override.enable()
    # Deferred to features/environment.py's after_scenario, which calls
    # every cleanup registered for this scenario. Without this, the
    # override would leak into the next scenario.
    context.scenario_cleanups.append(override.disable)


@when('GitHub sends a "{event_type}" event to "{path}" signed with "{secret}"')
def step_github_send_signed(context, event_type: str, path: str, secret: str) -> None:
    body = json.dumps(_DEFAULT_PAYLOAD).encode("utf-8")
    context.response = context.client.post(
        path,
        data=body,
        content_type="application/json",
        HTTP_X_HUB_SIGNATURE_256=_sign(secret, body),
        HTTP_X_GITHUB_EVENT=event_type,
        HTTP_X_GITHUB_DELIVERY="00000000-0000-0000-0000-000000000001",
    )


@when('GitHub sends a "{event_type}" event to "{path}" without a signature header')
def step_github_send_unsigned(context, event_type: str, path: str) -> None:
    body = json.dumps(_DEFAULT_PAYLOAD).encode("utf-8")
    context.response = context.client.post(
        path,
        data=body,
        content_type="application/json",
        HTTP_X_GITHUB_EVENT=event_type,
        HTTP_X_GITHUB_DELIVERY="00000000-0000-0000-0000-000000000002",
    )


@then('the event is recorded in the webhook log')
def step_event_recorded(context) -> None:
    from webhooks.models import WebhookEvent

    count = WebhookEvent.objects.count()
    assert count == 1, f"Expected exactly 1 webhook event, found {count}."


@then('the event is not recorded in the webhook log')
def step_event_not_recorded(context) -> None:
    from webhooks.models import WebhookEvent

    count = WebhookEvent.objects.count()
    assert count == 0, f"Expected no webhook events, found {count}."
