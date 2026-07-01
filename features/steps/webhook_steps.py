"""Steps for the GitHub webhook API.

The webhook endpoint touches no database state, so requests go to the
behave-django live server via context.base_url like the other relative
URL steps. Payloads mimic the shape of real GitHub deliveries.
"""
import hashlib
import hmac
import json
import os

import parse
import requests
from behave import given, register_type, when
from django.conf import settings


@parse.with_pattern(r'[^"]*')
def parse_quoted(text):
    return text


register_type(Q=parse_quoted)

EVENT_PAYLOADS = {
    "ping": {"zen": "Keep it logically awesome.", "hook_id": 1},
    "push": {"ref": "refs/heads/main", "commits": []},
}


def post_webhook(context, path, event, signature_header):
    body = json.dumps(EVENT_PAYLOADS.get(event, {})).encode()
    headers = {"Content-Type": "application/json", "X-GitHub-Event": event}
    if signature_header is not None:
        headers["X-Hub-Signature-256"] = signature_header
    context.webhook_body = body
    context.response = requests.post(
        f"{context.base_url}{path}", data=body, headers=headers, timeout=10
    )


@given('the webhook secret is configured from the environment variable "{variable}"')
def step_webhook_secret_configured(context, variable):
    secret = os.environ.get(variable, "")
    assert secret, f'environment variable "{variable}" is not set'
    assert settings.WEBHOOK_SECRET == secret, (
        f'settings.WEBHOOK_SECRET does not match the "{variable}" variable'
    )
    context.webhook_secret = secret


@when(
    'GitHub sends a POST request to "{path:Q}" with event "{event:Q}" and '
    "a payload signed with the webhook secret using HMAC SHA-256 in the "
    '"{header:Q}" header'
)
def step_signed_webhook_post(context, path, event, header):
    assert header == "X-Hub-Signature-256", f"unsupported signature header {header}"
    body = json.dumps(EVENT_PAYLOADS.get(event, {})).encode()
    digest = hmac.new(
        context.webhook_secret.encode(), body, hashlib.sha256
    ).hexdigest()
    post_webhook(context, path, event, f"sha256={digest}")


@when(
    'a client sends a POST request to "{path:Q}" with event "{event:Q}" and '
    'the header "{header:Q}" set to "{value:Q}"'
)
def step_webhook_post_with_header(context, path, event, header, value):
    assert header == "X-Hub-Signature-256", f"unsupported signature header {header}"
    post_webhook(context, path, event, value)


@when(
    'a client sends a POST request to "{path:Q}" with event "{event:Q}" and '
    'no "{header:Q}" header'
)
def step_webhook_post_without_header(context, path, event, header):
    assert header == "X-Hub-Signature-256", f"unsupported signature header {header}"
    post_webhook(context, path, event, None)
