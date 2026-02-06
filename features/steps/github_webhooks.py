import hashlib
import hmac
import json
from typing import Any

from behave import given, then, when
from django.conf import settings
from django.test import Client


@given('a webhook endpoint exists at "{endpoint}"')
def step_webhook_endpoint_exists(context, endpoint: str):
    """
    Verify that the webhook endpoint is configured.
    """
    context.webhook_endpoint = endpoint


@given("a webhook secret is configured")
def step_webhook_secret_configured(context):
    """
    Configure a webhook secret for testing.
    """
    context.webhook_secret = "test-webhook-secret-key"
    context.original_secret = settings.GITHUB_WEBHOOK_SECRET
    settings.GITHUB_WEBHOOK_SECRET = context.webhook_secret


@when('GitHub sends a push event webhook to "{endpoint}"')
def step_github_sends_push_webhook(context, endpoint: str):
    """
    Simulate GitHub sending a push event webhook.
    """
    client = Client()
    payload = {
        "ref": "refs/heads/main",
        "repository": {"name": "test-repo", "full_name": "test-org/test-repo"},
        "pusher": {"name": "testuser"},
    }
    payload_json = json.dumps(payload)

    response = client.post(
        endpoint,
        data=payload_json,
        content_type="application/json",
        HTTP_X_GITHUB_EVENT="push",
    )
    context.response = response


@when("GitHub sends a webhook with valid signature")
def step_github_sends_valid_signature(context):
    """
    Send a webhook with a valid HMAC-SHA256 signature.
    """
    client = Client()
    payload = {"test": "data"}
    payload_json = json.dumps(payload)
    payload_bytes = payload_json.encode("utf-8")

    signature = hmac.new(
        context.webhook_secret.encode("utf-8"), payload_bytes, hashlib.sha256
    ).hexdigest()

    endpoint = getattr(context, "webhook_endpoint", "/api/webhooks/github")
    response = client.post(
        endpoint,
        data=payload_json,
        content_type="application/json",
        HTTP_X_GITHUB_EVENT="ping",
        HTTP_X_HUB_SIGNATURE_256=f"sha256={signature}",
    )
    context.valid_signature_response = response


@when("GitHub sends a webhook with invalid signature")
def step_github_sends_invalid_signature(context):
    """
    Send a webhook with an invalid signature.
    """
    client = Client()
    payload = {"test": "data"}
    payload_json = json.dumps(payload)

    endpoint = getattr(context, "webhook_endpoint", "/api/webhooks/github")
    response = client.post(
        endpoint,
        data=payload_json,
        content_type="application/json",
        HTTP_X_GITHUB_EVENT="ping",
        HTTP_X_HUB_SIGNATURE_256="sha256=invalid_signature",
    )
    context.invalid_signature_response = response


@when("GitHub sends an issue opened event webhook")
def step_github_sends_issue_opened(context):
    """
    Simulate GitHub sending an issue opened event webhook.
    """
    if not hasattr(context, "original_secret"):
        context.original_secret = settings.GITHUB_WEBHOOK_SECRET
        settings.GITHUB_WEBHOOK_SECRET = ""

    client = Client()
    payload = {
        "action": "opened",
        "issue": {"number": 42, "title": "Test Issue", "state": "open"},
        "repository": {"name": "test-repo"},
    }
    payload_json = json.dumps(payload)

    response = client.post(
        "/api/webhooks/github",
        data=payload_json,
        content_type="application/json",
        HTTP_X_GITHUB_EVENT="issues",
    )
    context.response = response


@when("GitHub sends a pull request opened event webhook")
def step_github_sends_pr_opened(context):
    """
    Simulate GitHub sending a pull request opened event webhook.
    """
    if not hasattr(context, "original_secret"):
        context.original_secret = settings.GITHUB_WEBHOOK_SECRET
        settings.GITHUB_WEBHOOK_SECRET = ""

    client = Client()
    payload = {
        "action": "opened",
        "pull_request": {"number": 123, "title": "Test PR", "state": "open"},
        "repository": {"name": "test-repo"},
    }
    payload_json = json.dumps(payload)

    response = client.post(
        "/api/webhooks/github",
        data=payload_json,
        content_type="application/json",
        HTTP_X_GITHUB_EVENT="pull_request",
    )
    context.response = response


@then("the webhook is received successfully")
def step_webhook_received_successfully(context):
    """
    Verify that the webhook was received successfully.
    """
    assert hasattr(context, "response"), "No webhook response found"
    assert context.response.status_code == 200, (
        f"Expected status 200, got {context.response.status_code}"
    )


@then("the webhook is processed")
def step_webhook_processed(context):
    """
    Verify that the webhook with valid signature was processed.
    """
    assert hasattr(context, "valid_signature_response"), (
        "No valid signature response found"
    )
    assert context.valid_signature_response.status_code == 200, (
        f"Expected status 200, got {context.valid_signature_response.status_code}"
    )


@then("the webhook is rejected with status {status:d}")
def step_webhook_rejected(context, status: int):
    """
    Verify that the webhook was rejected with the expected status code.
    """
    assert hasattr(context, "invalid_signature_response"), (
        "No invalid signature response found"
    )
    assert context.invalid_signature_response.status_code == status, (
        f"Expected status {status}, got {context.invalid_signature_response.status_code}"
    )
    settings.GITHUB_WEBHOOK_SECRET = context.original_secret


@then("the service logs the issue creation")
def step_service_logs_issue_creation(context):
    """
    Verify that the service received and can log the issue creation.
    This checks that the webhook was processed successfully.
    """
    assert hasattr(context, "response"), "No response found"
    response_data = json.loads(context.response.content)
    assert response_data.get("status") == "success", "Webhook processing failed"
    if hasattr(context, "original_secret"):
        settings.GITHUB_WEBHOOK_SECRET = context.original_secret


@then("the service logs the pull request creation")
def step_service_logs_pr_creation(context):
    """
    Verify that the service received and can log the pull request creation.
    This checks that the webhook was processed successfully.
    """
    assert hasattr(context, "response"), "No response found"
    response_data = json.loads(context.response.content)
    assert response_data.get("status") == "success", "Webhook processing failed"
    if hasattr(context, "original_secret"):
        settings.GITHUB_WEBHOOK_SECRET = context.original_secret
