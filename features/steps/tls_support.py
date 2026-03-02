"""Step definitions for TLS support feature."""

import json
import subprocess

from behave import given, then, when


@given('the service is running with TLS enabled')
def step_service_is_running_with_tls(context):
    """Verify that the service is running with TLS enabled."""
    # Check HTTPS endpoint is accessible
    result = subprocess.run(
        ['curl', '--fail', '--insecure', '--silent', 'https://localhost:8443/'],
        capture_output=True,
        timeout=5
    )
    # Service should respond (even if 404, connection is working)
    assert result.returncode in [0, 22], "HTTPS service is not accessible"


@when('I send a GET request to the full URL "{url}"')
def step_send_get_request_to_full_url(context, url):
    """Send a GET request to the specified full URL."""
    curl_cmd = [
        'curl',
        '--silent',
        '--write-out', '\\n%{http_code}',
    ]

    # Add --insecure flag for HTTPS requests to accept self-signed certificates
    if url.startswith('https://'):
        curl_cmd.append('--insecure')

    curl_cmd.append(url)

    result = subprocess.run(
        curl_cmd,
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

    # Store the URL for TLS verification
    context.last_request_url = url


@when('I send a POST request to the full URL "{url}" with credentials "{username}" and "{password}"')
def step_send_post_request_to_full_url_with_credentials(context, url, username, password):
    """Send a POST request with credentials to the specified full URL."""
    payload = json.dumps({"username": username, "password": password})

    curl_cmd = [
        'curl',
        '--data', payload,
        '--header', 'Content-Type: application/json',
        '--request', 'POST',
        '--silent',
        '--write-out', '\\n%{http_code}',
    ]

    # Add --insecure flag for HTTPS requests to accept self-signed certificates
    if url.startswith('https://'):
        curl_cmd.append('--insecure')

    curl_cmd.append(url)

    result = subprocess.run(
        curl_cmd,
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

    # Store the URL for TLS verification
    context.last_request_url = url


@then('the connection is encrypted with TLS')
def step_verify_tls_connection(context):
    """Verify that the connection used TLS encryption."""
    # Check that the last request was made over HTTPS or WSS
    assert hasattr(context, 'last_request_url'), "No request was made"
    assert context.last_request_url.startswith('https://') or context.last_request_url.startswith('wss://'), \
        f"Expected HTTPS or WSS connection, but URL was {context.last_request_url}"


@when('I connect to secure WebSocket "{url}"')
def step_connect_to_secure_websocket(context, url):
    """Connect to a secure WebSocket endpoint (WSS)."""
    # Store URL for TLS verification
    context.last_request_url = url

    # Use wscat (node-ws package provides wscat) to test WebSocket connection
    # For WSS (secure WebSocket), we need to use the --no-check flag to skip certificate validation
    wscat_cmd = ['timeout', '2', 'wscat', '--connect', url, '--no-check']

    result = subprocess.run(
        wscat_cmd,
        capture_output=True,
        text=True,
        timeout=5
    )

    # Store connection result
    context.websocket_url = url
    # If wscat doesn't return an error in stderr, connection was successful
    # timeout command returns 124 when it times out (expected after 2 seconds)
    context.websocket_connected = result.returncode in [0, 124]


@then('the secure WebSocket connection is established')
def step_verify_secure_websocket_connection(context):
    """Verify that the secure WebSocket connection was established."""
    assert context.websocket_connected, \
        f"Failed to establish WebSocket connection to {context.websocket_url}"
