"""
Step definitions for Feature 008: GitHub Webhook Integration
"""
import json
import hmac
import hashlib
from behave import given, when, then
from django.test import Client
from django.http import HttpRequest


def _create_signature(payload_body, secret):
    """
    Helper: Create GitHub webhook signature.
    """
    if isinstance(payload_body, str):
        payload_body = payload_body.encode('utf-8')

    signature = hmac.new(
        secret.encode('utf-8'),
        payload_body,
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"


def _get_valid_payload():
    """
    Helper: Return a valid GitHub webhook payload.
    """
    return {
        'action': 'opened',
        'pull_request': {
            'id': 1,
            'number': 1,
            'title': 'Test Pull Request',
            'body': 'This is a test PR for webhook integration',
            'user': {
                'login': 'testuser',
                'id': 123
            },
            'created_at': '2024-01-18T12:00:00Z',
            'updated_at': '2024-01-18T12:00:00Z'
        },
        'repository': {
            'id': 456,
            'name': 'test-repo',
            'full_name': 'testuser/test-repo',
            'owner': {
                'login': 'testuser'
            }
        }
    }


@given('the webhook endpoint exists')
def step_webhook_endpoint_exists(context):
    """
    Verify that the webhook endpoint exists.
    """
    if not hasattr(context, 'client'):
        context.client = Client()

    # Just initialize the client - endpoint is defined in views
    context.webhook_endpoint = '/api/webhooks/github/'


@given('a valid GitHub webhook payload')
def step_valid_webhook_payload(context):
    """
    Create a valid GitHub webhook payload.
    """
    context.webhook_payload = _get_valid_payload()
    context.webhook_secret = 'test-webhook-secret'


@given('an invalid GitHub webhook payload')
def step_invalid_webhook_payload(context):
    """
    Create an invalid GitHub webhook payload (missing required fields).
    """
    context.webhook_payload = {
        'invalid_field': 'test'
    }
    context.webhook_secret = 'test-webhook-secret'


@given('a GitHub webhook with X-Hub-Signature header')
def step_webhook_with_signature(context):
    """
    Create a GitHub webhook payload with signature header.
    """
    context.webhook_payload = _get_valid_payload()
    context.webhook_secret = 'test-webhook-secret'

    # Create the signature
    payload_json = json.dumps(context.webhook_payload)
    signature = _create_signature(payload_json, context.webhook_secret)

    if not hasattr(context, 'webhook_headers'):
        context.webhook_headers = {}

    context.webhook_headers['X-Hub-Signature-256'] = signature




@when('I make a POST request to the webhook endpoint')
def step_post_to_webhook_endpoint(context):
    """
    Make a POST request to the webhook endpoint.
    """
    if not hasattr(context, 'client'):
        context.client = Client()

    if not hasattr(context, 'webhook_headers'):
        context.webhook_headers = {}

    context.webhook_response = context.client.post(
        '/api/webhooks/github/',
        data=json.dumps({}),
        content_type='application/json',
        **context.webhook_headers
    )

    context.webhook_response_status = context.webhook_response.status_code


@when('I POST the payload to the webhook endpoint')
def step_post_payload_to_webhook(context):
    """
    POST the webhook payload to the endpoint.
    """
    if not hasattr(context, 'client'):
        context.client = Client()

    if not hasattr(context, 'webhook_headers'):
        context.webhook_headers = {}

    payload_json = json.dumps(context.webhook_payload)

    context.webhook_response = context.client.post(
        '/api/webhooks/github/',
        data=payload_json,
        content_type='application/json',
        **context.webhook_headers
    )

    context.webhook_response_status = context.webhook_response.status_code

    try:
        context.webhook_response_data = json.loads(context.webhook_response.content)
    except:
        context.webhook_response_data = None


@when('I POST the webhook payload')
def step_post_webhook_payload(context):
    """
    POST the webhook payload with signature validation.
    """
    # This is the same as "I POST the payload to the webhook endpoint"
    # with the signature already prepared in headers
    step_post_payload_to_webhook(context)


@when('I POST to the webhook endpoint')
def step_post_to_webhook(context):
    """
    POST to the webhook endpoint (generic).
    """
    step_post_payload_to_webhook(context)


@then('the request is accepted with status 200 OK')
def step_request_accepted_200(context):
    """
    Verify the request is accepted with status 200 OK.
    """
    assert hasattr(context, 'webhook_response_status'), \
        "No webhook response status found"
    assert context.webhook_response_status == 200, \
        f"Expected status 200, got {context.webhook_response_status}: {context.webhook_response.content}"


@then('the payload is processed successfully')
def step_payload_processed_successfully(context):
    """
    Verify the payload is processed successfully.
    """
    assert hasattr(context, 'webhook_response_status'), \
        "No webhook response status found"
    assert context.webhook_response_status in [200, 201, 202], \
        f"Expected success status, got {context.webhook_response_status}"

    # Check if response indicates successful processing
    if hasattr(context, 'webhook_response_data') and context.webhook_response_data:
        assert 'success' in context.webhook_response_data or \
               'message' in context.webhook_response_data or \
               context.webhook_response_status == 200, \
            f"Response does not indicate success: {context.webhook_response_data}"


@then('the request fails with a validation error')
def step_request_fails_validation(context):
    """
    Verify the request fails with a validation error.
    """
    assert hasattr(context, 'webhook_response_status'), \
        "No webhook response status found"
    assert context.webhook_response_status in [400, 422], \
        f"Expected validation error (400/422), got {context.webhook_response_status}"

    # Check if response indicates validation error
    if hasattr(context, 'webhook_response_data') and context.webhook_response_data:
        assert 'error' in context.webhook_response_data or \
               'detail' in context.webhook_response_data or \
               'message' in context.webhook_response_data, \
            f"Response does not indicate error: {context.webhook_response_data}"


@then('the signature is validated against the webhook secret')
def step_signature_validated(context):
    """
    Verify the signature is validated against the webhook secret.
    """
    # If we got here without error and have a signature header,
    # the validation passed
    assert hasattr(context, 'webhook_headers'), \
        "No webhook headers found"
    assert 'X-Hub-Signature-256' in context.webhook_headers or \
           'X-Hub-Signature' in context.webhook_headers, \
        "No signature header found in request"

    # Response should indicate successful validation
    assert hasattr(context, 'webhook_response_status'), \
        "No webhook response status found"
    assert context.webhook_response_status in [200, 201, 202], \
        f"Signature validation failed, got status {context.webhook_response_status}"


@then('invalid signatures are rejected')
def step_invalid_signatures_rejected(context):
    """
    Verify that invalid signatures are rejected.
    """
    if not hasattr(context, 'client'):
        context.client = Client()

    # Create payload with invalid signature
    payload_json = json.dumps(context.webhook_payload)
    invalid_signature = 'sha256=invalidsignaturevalue'

    response = context.client.post(
        '/api/webhooks/github/',
        data=payload_json,
        content_type='application/json',
        HTTP_X_HUB_SIGNATURE_256=invalid_signature
    )

    # Invalid signature should be rejected (401 or 403)
    assert response.status_code in [401, 403, 400], \
        f"Invalid signature should be rejected, got {response.status_code}"


@then('the webhook is processed successfully')
def step_webhook_processed_successfully(context):
    """
    Verify the webhook is processed successfully without authentication.
    """
    assert hasattr(context, 'webhook_response_status'), \
        "No webhook response status found"
    assert context.webhook_response_status in [200, 201, 202], \
        f"Expected successful processing, got {context.webhook_response_status}"
