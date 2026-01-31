"""
Step definitions for Feature 008: GitHub Webhooks Integration
"""
import hmac
import hashlib
import json
from behave import given, when, then
from django.test import Client
from apps.webhooks.models import WebhookEvent


# Default webhook secret for testing
WEBHOOK_SECRET = 'test-webhook-secret'


def create_github_signature(payload, secret):
    """
    Create a GitHub-style HMAC SHA256 signature.
    """
    if isinstance(payload, dict):
        payload = json.dumps(payload).encode('utf-8')
    elif isinstance(payload, str):
        payload = payload.encode('utf-8')

    mac = hmac.new(
        secret.encode('utf-8'),
        msg=payload,
        digestmod=hashlib.sha256
    )
    return f'sha256={mac.hexdigest()}'


@when('GitHub sends a push event webhook with a valid signature')
def step_github_push_valid_signature(context):
    """
    Send a push event webhook with valid signature.
    """
    if not hasattr(context, 'client'):
        context.client = Client()

    payload = {
        'ref': 'refs/heads/main',
        'before': '0000000000000000000000000000000000000000',
        'after': '1111111111111111111111111111111111111111',
        'repository': {
            'name': 'test-repo',
            'full_name': 'user/test-repo'
        },
        'pusher': {
            'name': 'test-user',
            'email': 'test@example.com'
        }
    }

    payload_json = json.dumps(payload)
    signature = create_github_signature(payload_json, WEBHOOK_SECRET)

    context.response = context.client.post(
        '/api/webhooks/github',
        data=payload_json,
        content_type='application/json',
        HTTP_X_GITHUB_EVENT='push',
        HTTP_X_GITHUB_DELIVERY='test-delivery-id-push',
        HTTP_X_HUB_SIGNATURE_256=signature
    )

    try:
        context.response_data = json.loads(context.response.content)
    except (json.JSONDecodeError, ValueError):
        context.response_data = None


@when('GitHub sends a push event webhook with an invalid signature')
def step_github_push_invalid_signature(context):
    """
    Send a push event webhook with invalid signature.
    """
    if not hasattr(context, 'client'):
        context.client = Client()

    payload = {
        'ref': 'refs/heads/main',
        'repository': {
            'name': 'test-repo'
        }
    }

    payload_json = json.dumps(payload)
    # Create invalid signature
    invalid_signature = 'sha256=invalid_signature_that_wont_match'

    context.response = context.client.post(
        '/api/webhooks/github',
        data=payload_json,
        content_type='application/json',
        HTTP_X_GITHUB_EVENT='push',
        HTTP_X_GITHUB_DELIVERY='test-delivery-id-invalid',
        HTTP_X_HUB_SIGNATURE_256=invalid_signature
    )

    try:
        context.response_data = json.loads(context.response.content)
    except (json.JSONDecodeError, ValueError):
        context.response_data = None


@when('GitHub sends a pull request event webhook with a valid signature')
def step_github_pr_valid_signature(context):
    """
    Send a pull request event webhook with valid signature.
    """
    if not hasattr(context, 'client'):
        context.client = Client()

    payload = {
        'action': 'opened',
        'number': 1,
        'pull_request': {
            'id': 12345,
            'title': 'Test PR',
            'state': 'open',
            'user': {
                'login': 'test-user'
            }
        },
        'repository': {
            'name': 'test-repo',
            'full_name': 'user/test-repo'
        }
    }

    payload_json = json.dumps(payload)
    signature = create_github_signature(payload_json, WEBHOOK_SECRET)

    context.response = context.client.post(
        '/api/webhooks/github',
        data=payload_json,
        content_type='application/json',
        HTTP_X_GITHUB_EVENT='pull_request',
        HTTP_X_GITHUB_DELIVERY='test-delivery-id-pr',
        HTTP_X_HUB_SIGNATURE_256=signature
    )

    try:
        context.response_data = json.loads(context.response.content)
    except (json.JSONDecodeError, ValueError):
        context.response_data = None


@then('the webhook event is logged in the system')
def step_webhook_event_logged(context):
    """
    Verify the webhook event was logged.
    """
    # Check that a WebhookEvent was created
    assert WebhookEvent.objects.count() > 0, "No webhook events were logged"


@given('a GitHub push event was previously received')
def step_github_push_previously_received(context):
    """
    Ensure a GitHub push event exists in the system.
    """
    # First clear any existing events to ensure clean state
    WebhookEvent.objects.all().delete()

    # Create a push event
    WebhookEvent.objects.create(
        event_type='push',
        delivery_id='previous-push-event-id',
        payload={
            'ref': 'refs/heads/main',
            'repository': {'name': 'test-repo'}
        }
    )


@when('I request the list of webhook events')
def step_request_webhook_events(context):
    """
    Request the list of webhook events.
    """
    assert hasattr(context, 'access_token') and context.access_token is not None, \
        "No access token available"

    context.response = context.client.get(
        '/api/webhooks/github/events',
        HTTP_AUTHORIZATION=f'Bearer {context.access_token}',
        content_type='application/json'
    )

    try:
        context.response_data = json.loads(context.response.content)
    except (json.JSONDecodeError, ValueError):
        context.response_data = None


@then('the response contains webhook event details')
def step_response_contains_webhook_event_details(context):
    """
    Verify the response contains webhook event details.
    """
    assert context.response_data is not None, "Response data is None"

    # Response should be a list or contain a 'results' key (paginated)
    if isinstance(context.response_data, list):
        events = context.response_data
    elif isinstance(context.response_data, dict) and 'results' in context.response_data:
        events = context.response_data['results']
    else:
        events = [context.response_data]

    assert len(events) > 0, "No webhook events in response"

    event = events[0]
    assert 'event_type' in event, "Event type not in response"
    assert 'delivery_id' in event, "Delivery ID not in response"
    assert 'payload' in event, "Payload not in response"


@then('the response contains header "{header_name}" with value "{header_value}"')
def step_response_contains_header(context, header_name, header_value):
    """
    Verify the response contains a specific header with expected value.
    """
    actual_value = context.response.get(header_name)
    assert actual_value is not None, f"Header '{header_name}' not found in response"
    assert actual_value == header_value, \
        f"Expected header '{header_name}' to be '{header_value}', got '{actual_value}'"
