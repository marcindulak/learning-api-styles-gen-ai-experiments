"""Step definitions for GitHub webhook integration."""

import hashlib
import hmac
import json
import os
import subprocess
import time

from behave import given, then, when

from src.weather.models import City, WebhookEvent


@when('GitHub sends a push webhook to "{endpoint}" with payload:')
def step_github_push_webhook_with_payload(context, endpoint):
    """Send a GitHub push webhook with payload from table."""
    payload = {}
    for row in context.table:
        key = row.cells[0]
        value = row.cells[1]
        payload[key] = value

    payload_json = json.dumps(payload)

    result = subprocess.run(
        [
            'curl',
            '--data', payload_json,
            '--header', 'Content-Type: application/json',
            '--header', 'X-GitHub-Event: push',
            '--request', 'POST',
            '--silent',
            '--write-out', '\\n%{http_code}',
            f'http://localhost:8000{endpoint}'
        ],
        capture_output=True,
        text=True,
        timeout=10
    )

    lines = result.stdout.strip().split('\n')
    context.response_status_code = int(lines[-1])
    context.response_body = '\n'.join(lines[:-1]) if len(lines) > 1 else ''

    try:
        context.response_json = json.loads(context.response_body) if context.response_body else {}
    except json.JSONDecodeError:
        context.response_json = {}


@then('the webhook event is logged')
def step_webhook_event_logged(context):
    """Verify that the webhook event was logged in the database."""
    time.sleep(0.5)
    event_count = WebhookEvent.objects.count()
    assert event_count > 0, "No webhook events found in database"


@given('a webhook secret is configured')
def step_webhook_secret_configured(context):
    """Set up a webhook secret for signature validation."""
    context.webhook_secret = 'test_webhook_secret_123'
    subprocess.run(
        [
            'curl',
            '--data', json.dumps({'GITHUB_WEBHOOK_SECRET': context.webhook_secret}),
            '--header', 'Content-Type: application/json',
            '--request', 'POST',
            '--silent',
            'http://localhost:8000/api/test/set-env/'
        ],
        capture_output=True,
        text=True,
        timeout=10
    )


@when('GitHub sends a webhook with valid signature')
def step_github_webhook_valid_signature(context):
    """Send a webhook with a valid HMAC-SHA256 signature."""
    payload = {"ref": "refs/heads/main", "repository": "test-repo"}
    payload_json = json.dumps(payload)
    payload_bytes = payload_json.encode('utf-8')

    secret = context.webhook_secret.encode('utf-8')
    signature = hmac.new(secret, payload_bytes, hashlib.sha256).hexdigest()

    result = subprocess.run(
        [
            'curl',
            '--data', payload_json,
            '--header', 'Content-Type: application/json',
            '--header', 'X-GitHub-Event: push',
            '--header', f'X-Hub-Signature-256: sha256={signature}',
            '--request', 'POST',
            '--silent',
            '--write-out', '\\n%{http_code}',
            'http://localhost:8000/webhooks/github'
        ],
        capture_output=True,
        text=True,
        timeout=10
    )

    lines = result.stdout.strip().split('\n')
    context.response_status_code = int(lines[-1])
    context.response_body = '\n'.join(lines[:-1]) if len(lines) > 1 else ''


@then('the webhook is processed')
def step_webhook_processed(context):
    """Verify that the webhook was processed."""
    time.sleep(0.5)
    processed_count = WebhookEvent.objects.filter(processed=True).count()
    assert processed_count > 0, "No processed webhook events found"


@when('a webhook is sent with invalid signature')
def step_webhook_invalid_signature(context):
    """Send a webhook with an invalid signature."""
    payload = {"ref": "refs/heads/main", "repository": "test-repo"}
    payload_json = json.dumps(payload)

    result = subprocess.run(
        [
            'curl',
            '--data', payload_json,
            '--header', 'Content-Type: application/json',
            '--header', 'X-GitHub-Event: push',
            '--header', 'X-Hub-Signature-256: sha256=invalid_signature_here',
            '--request', 'POST',
            '--silent',
            '--write-out', '\\n%{http_code}',
            'http://localhost:8000/webhooks/github'
        ],
        capture_output=True,
        text=True,
        timeout=10
    )

    lines = result.stdout.strip().split('\n')
    context.response_status_code = int(lines[-1])
    context.response_body = '\n'.join(lines[:-1]) if len(lines) > 1 else ''


@then('the webhook is not processed')
def step_webhook_not_processed(context):
    """Verify that the webhook was not processed (due to invalid signature)."""
    time.sleep(0.5)
    event_count = WebhookEvent.objects.count()
    assert event_count == 0, "Webhook event should not have been created with invalid signature"


@when('GitHub sends a push webhook to "{endpoint}" with tag "{tag}"')
def step_github_push_webhook_with_tag(context, endpoint, tag):
    """Send a GitHub push webhook with a specific tag/ref."""
    subprocess.run(
        [
            'curl',
            '--data', json.dumps({'test_mode': 'available'}),
            '--header', 'Content-Type: application/json',
            '--request', 'POST',
            '--silent',
            f'http://localhost:8000/api/test/set-mode/'
        ],
        capture_output=True,
        text=True,
        timeout=10
    )

    payload = {
        "ref": f"refs/tags/{tag}",
        "repository": "test-repo"
    }
    payload_json = json.dumps(payload)

    result = subprocess.run(
        [
            'curl',
            '--data', payload_json,
            '--header', 'Content-Type: application/json',
            '--header', 'X-GitHub-Event: push',
            '--request', 'POST',
            '--silent',
            '--write-out', '\\n%{http_code}',
            f'http://localhost:8000{endpoint}'
        ],
        capture_output=True,
        text=True,
        timeout=15
    )

    lines = result.stdout.strip().split('\n')
    context.response_status_code = int(lines[-1])
    context.response_body = '\n'.join(lines[:-1]) if len(lines) > 1 else ''


@then('weather data fetch is triggered for all cities')
def step_weather_data_fetch_triggered(context):
    """Verify that weather data fetch was triggered by checking for weather data updates."""
    from src.weather.models import CurrentWeather, WeatherForecast
    time.sleep(1)

    current_weather_count = CurrentWeather.objects.count()
    forecast_count = WeatherForecast.objects.count()

    assert current_weather_count > 0 or forecast_count > 0, \
        "Weather data fetch should have created weather records"


@when('GitHub sends any webhook to "{endpoint}"')
def step_github_sends_any_webhook(context, endpoint):
    """Send a generic GitHub webhook."""
    payload = {
        "action": "opened",
        "repository": "test-repo"
    }
    payload_json = json.dumps(payload)

    result = subprocess.run(
        [
            'curl',
            '--data', payload_json,
            '--header', 'Content-Type: application/json',
            '--header', 'X-GitHub-Event: issues',
            '--request', 'POST',
            '--silent',
            '--write-out', '\\n%{http_code}',
            f'http://localhost:8000{endpoint}'
        ],
        capture_output=True,
        text=True,
        timeout=10
    )

    lines = result.stdout.strip().split('\n')
    context.response_status_code = int(lines[-1])
    context.response_body = '\n'.join(lines[:-1]) if len(lines) > 1 else ''


@then('the webhook event is stored with timestamp, event type, and payload')
def step_webhook_stored_with_details(context):
    """Verify webhook event contains required fields."""
    time.sleep(0.5)
    events = WebhookEvent.objects.all()
    assert events.count() > 0, "No webhook events found"

    event = events.first()
    assert event.timestamp is not None, "Webhook event should have timestamp"
    assert event.event_type is not None, "Webhook event should have event_type"
    assert event.payload is not None, "Webhook event should have payload"
    assert isinstance(event.payload, dict), "Webhook payload should be a dict"
