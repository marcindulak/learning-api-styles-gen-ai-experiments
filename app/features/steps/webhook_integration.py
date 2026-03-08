"""
Step definitions for GitHub webhook integration.
"""
import hashlib
import hmac
import json
import subprocess
from behave import given, when, then


@given('a webhook secret is configured')
def step_configure_webhook_secret(context):
    """Configure a webhook secret for signature validation."""
    context.webhook_secret = 'test_secret_key'
    payload = json.dumps({
        "key": "GITHUB_WEBHOOK_SECRET",
        "value": context.webhook_secret
    })
    cmd = [
        "curl",
        "--data", payload,
        "--header", "Content-Type: application/json",
        "--request", "POST",
        "--silent",
        "http://localhost:8000/api/test/set-env/"
    ]
    subprocess.run(cmd, check=True, capture_output=True)


@when('GitHub sends a webhook POST to "{endpoint}"')
def step_send_webhook(context, endpoint):
    """Send a GitHub webhook POST request."""
    payload_data = {
        "ref": "refs/heads/main",
        "commits": []
    }

    payload = json.dumps(payload_data)

    cmd = [
        "curl",
        "--data", payload,
        "--header", "Content-Type: application/json",
        "--header", "X-GitHub-Event: push",
        "--request", "POST",
        "--silent",
        "--write-out", "\n%{http_code}",
        f"http://localhost:8000{endpoint}"
    ]

    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    output_lines = result.stdout.strip().split('\n')

    if len(output_lines) >= 2:
        context.response_body = '\n'.join(output_lines[:-1])
        context.response_status_code = int(output_lines[-1])
    else:
        context.response_status_code = int(output_lines[0])
        context.response_body = ""


@when('GitHub sends a signed webhook POST to "{endpoint}"')
def step_send_signed_webhook(context, endpoint):
    """Send a signed GitHub webhook POST request."""
    payload_data = {
        "ref": "refs/heads/main",
        "commits": []
    }

    payload = json.dumps(payload_data)
    payload_bytes = payload.encode('utf-8')

    secret = context.webhook_secret.encode('utf-8')
    hash_object = hmac.new(secret, msg=payload_bytes, digestmod=hashlib.sha256)
    signature = 'sha256=' + hash_object.hexdigest()

    cmd = [
        "curl",
        "--data", payload,
        "--header", "Content-Type: application/json",
        "--header", "X-GitHub-Event: push",
        "--header", f"X-Hub-Signature-256: {signature}",
        "--request", "POST",
        "--silent",
        "--write-out", "\n%{http_code}",
        f"http://localhost:8000{endpoint}"
    ]

    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    output_lines = result.stdout.strip().split('\n')

    if len(output_lines) >= 2:
        context.response_body = '\n'.join(output_lines[:-1])
        context.response_status_code = int(output_lines[-1])
    else:
        context.response_status_code = int(output_lines[0])
        context.response_body = ""


@when('an invalid signed webhook POST is sent to "{endpoint}"')
def step_send_invalid_signed_webhook(context, endpoint):
    """Send a webhook POST request with an invalid signature."""
    payload_data = {
        "ref": "refs/heads/main",
        "commits": []
    }

    payload = json.dumps(payload_data)
    invalid_signature = 'sha256=invalid_signature_hash'

    cmd = [
        "curl",
        "--data", payload,
        "--header", "Content-Type: application/json",
        "--header", "X-GitHub-Event: push",
        "--header", f"X-Hub-Signature-256: {invalid_signature}",
        "--request", "POST",
        "--silent",
        "--write-out", "\n%{http_code}",
        f"http://localhost:8000{endpoint}"
    ]

    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    output_lines = result.stdout.strip().split('\n')

    if len(output_lines) >= 2:
        context.response_body = '\n'.join(output_lines[:-1])
        context.response_status_code = int(output_lines[-1])
    else:
        context.response_status_code = int(output_lines[0])
        context.response_body = ""


@when('GitHub sends a webhook for a "{event_marker}" event')
def step_send_webhook_with_marker(context, event_marker):
    """Send a webhook with a specific event marker in the ref or commit message."""
    payload_data = {
        "ref": f"refs/heads/{event_marker}",
        "commits": [
            {
                "message": f"Update data with {event_marker} marker"
            }
        ]
    }

    payload = json.dumps(payload_data)

    cmd = [
        "curl",
        "--data", payload,
        "--header", "Content-Type: application/json",
        "--header", "X-GitHub-Event: push",
        "--request", "POST",
        "--silent",
        "--write-out", "\n%{http_code}",
        "http://localhost:8000/api/webhooks/github/"
    ]

    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    output_lines = result.stdout.strip().split('\n')

    if len(output_lines) >= 2:
        context.response_body = '\n'.join(output_lines[:-1])
        context.response_status_code = int(output_lines[-1])
    else:
        context.response_status_code = int(output_lines[0])
        context.response_body = ""


@when('GitHub sends {count:d} webhook events')
def step_send_multiple_webhooks(context, count):
    """Send multiple webhook events."""
    for i in range(count):
        payload_data = {
            "ref": f"refs/heads/branch-{i}",
            "commits": []
        }

        payload = json.dumps(payload_data)

        cmd = [
            "curl",
            "--data", payload,
            "--header", "Content-Type: application/json",
            "--header", "X-GitHub-Event: push",
            "--request", "POST",
            "--silent",
            "--write-out", "\n%{http_code}",
            "http://localhost:8000/api/webhooks/github/"
        ]

        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        output_lines = result.stdout.strip().split('\n')

        if len(output_lines) >= 2:
            context.response_body = '\n'.join(output_lines[:-1])
            context.response_status_code = int(output_lines[-1])
        else:
            context.response_status_code = int(output_lines[0])
            context.response_body = ""


@then('the webhook event is logged')
def step_verify_webhook_logged(context):
    """Verify that the webhook event is logged in the database."""
    from weather.models import WebhookEvent

    webhook_events = WebhookEvent.objects.all()
    assert webhook_events.exists(), "No webhook events found in database"


@then('the signature is validated')
def step_verify_signature_validated(context):
    """Verify that the signature was validated successfully."""
    assert context.response_status_code == 200, f"Expected status 200, got {context.response_status_code}"


@then('weather data for all cities is refreshed')
def step_verify_data_refreshed(context):
    """Verify that weather data was refreshed for all cities."""
    from weather.models import City, CurrentWeather, WebhookEvent

    webhook_events = WebhookEvent.objects.filter(processed=True)
    assert webhook_events.exists(), "No processed webhook events found"

    cities = City.objects.all()
    for city in cities:
        current_weather = CurrentWeather.objects.filter(city=city).first()
        assert current_weather is not None, f"No current weather data found for {city.name}"


@then('{count:d} webhook events are logged in the database')
def step_verify_webhook_count(context, count):
    """Verify that the expected number of webhook events are logged."""
    from weather.models import WebhookEvent

    webhook_events = WebhookEvent.objects.all()
    actual_count = webhook_events.count()
    assert actual_count == count, f"Expected {count} webhook events, found {actual_count}"
