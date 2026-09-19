import hashlib
import hmac
import json
import uuid

from behave import given, then, when
from common_steps import _client_for
from django.test import override_settings

from webhooks.models import GitHubWebhookEvent


def _header_kwarg(header_name):
    return "HTTP_" + header_name.upper().replace("-", "_")


def _build_payload(context, event_type):
    context.webhook_body = json.dumps({"ref": "refs/heads/main", "zen": event_type}).encode()
    context.webhook_delivery_id = str(uuid.uuid4())


def _sign(context, secret):
    digest = hmac.new(secret.encode(), msg=context.webhook_body, digestmod=hashlib.sha256).hexdigest()
    context.webhook_signature_header = f"sha256={digest}"


@given('the GitHub webhook secret is configured as "{secret}"')
def step_given_webhook_secret(context, secret):
    override = override_settings(WEBHOOK_SECRET=secret)
    override.enable()
    context.add_cleanup(override.disable)


@given('a "{event_type}" event payload signed with the secret "{secret}" using HMAC-SHA256')
def step_given_signed_payload(context, event_type, secret):
    _build_payload(context, event_type)
    _sign(context, secret)


@given('a "{event_type}" event payload with no "X-Hub-Signature-256" header')
def step_given_unsigned_payload(context, event_type):
    _build_payload(context, event_type)
    context.webhook_signature_header = None


@given('a malformed JSON body signed with the secret "{secret}" using HMAC-SHA256')
def step_given_malformed_json_payload(context, secret):
    context.webhook_body = b"{not valid json"
    context.webhook_delivery_id = str(uuid.uuid4())
    _sign(context, secret)


@when('a client sends "POST /api/webhooks/github" with the signed payload and header "{header}: {value}"')
@when('a client sends "POST /api/webhooks/github" with the unsigned payload and header "{header}: {value}"')
def step_when_sends_webhook(context, header, value):
    extra = {
        _header_kwarg(header): value,
        _header_kwarg("X-GitHub-Delivery"): context.webhook_delivery_id,
    }
    if context.webhook_signature_header is not None:
        extra[_header_kwarg("X-Hub-Signature-256")] = context.webhook_signature_header
    context.last_response = _client_for(context, "anonymous").post(
        "/api/webhooks/github",
        data=context.webhook_body,
        content_type="application/json",
        **extra,
    )


@then('an event is recorded with type "{event_type}" and a delivery id')
def step_then_event_recorded(context, event_type):
    event = GitHubWebhookEvent.objects.get(delivery_id=context.webhook_delivery_id)
    assert event.event_type == event_type
    assert event.delivery_id


@then("no event is recorded")
def step_then_no_event_recorded(context):
    assert not GitHubWebhookEvent.objects.exists()


@then('exactly {count:d} event is recorded with type "{event_type}"')
def step_then_exactly_n_events_recorded(context, count, event_type):
    assert GitHubWebhookEvent.objects.filter(event_type=event_type).count() == count
