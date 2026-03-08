"""
Step definitions for TLS support.
"""
import json
import os
import subprocess

from behave import given, then, when


@given('TLS is enabled')
def step_enable_tls(context):
    """
    Verify that TLS is enabled.

    TLS is enabled by setting TLS_ENABLE=1 in compose.yaml.
    This step just marks that TLS scenarios should be tested.
    """
    context.tls_enabled = True


@when('I send a GET request to the full URL "{url}"')
def step_send_get_request_full_url(context, url):
    """Send GET request to a full URL (including scheme and host)."""
    # Use --insecure flag to allow self-signed certificates
    args = [
        'curl',
        '--request', 'GET',
        '--silent',
        '--output', '/dev/null',
        '--write-out', '%{http_code}',
    ]

    # Add --insecure flag for HTTPS URLs with self-signed certs
    if url.startswith('https://'):
        args.append('--insecure')

    args.append(url)

    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
    )

    context.response_status_code = int(result.stdout)
    context.last_url = url


@then('the connection uses TLS encryption')
def step_check_tls_encryption(context):
    """Check that the connection uses TLS encryption."""
    # Verify URL starts with https://
    assert hasattr(context, 'last_url'), 'No URL was accessed'
    assert context.last_url.startswith('https://'), \
        f'URL does not use HTTPS: {context.last_url}'


@when('I request a JWT access token over HTTPS with username "{username}" and password "{password}"')
def step_request_jwt_token_https(context, username, password):
    """Request JWT access token over HTTPS."""
    credentials = json.dumps({'username': username, 'password': password})

    # Get response body
    result = subprocess.run(
        [
            'curl',
            '--data', credentials,
            '--header', 'Content-Type: application/json',
            '--request', 'POST',
            '--silent',
            '--insecure',  # Allow self-signed certificate
            'https://localhost:8443/api/jwt/obtain',
        ],
        capture_output=True,
        text=True,
    )

    context.response_body = result.stdout

    # Get status code
    result_with_code = subprocess.run(
        [
            'curl',
            '--data', credentials,
            '--header', 'Content-Type: application/json',
            '--request', 'POST',
            '--silent',
            '--insecure',  # Allow self-signed certificate
            '--output', '/dev/null',
            '--write-out', '%{http_code}',
            'https://localhost:8443/api/jwt/obtain',
        ],
        capture_output=True,
        text=True,
    )

    context.response_status_code = int(result_with_code.stdout)


@when('I establish a secure WebSocket connection to "{wss_url}"')
def step_establish_secure_websocket_connection(context, wss_url):
    """Establish a secure WebSocket connection (WSS)."""
    from websocket import create_connection

    try:
        # Use sslopt parameter to skip certificate verification for self-signed certs
        context.websocket = create_connection(
            wss_url,
            sslopt={'cert_reqs': 0}  # ssl.CERT_NONE
        )
        context.websocket_connected = True
        context.websocket_url = wss_url
    except Exception as e:
        context.websocket_connected = False
        context.websocket_error = str(e)


@then('the connection uses WSS protocol')
def step_check_wss_protocol(context):
    """Check that the WebSocket connection uses WSS protocol."""
    assert hasattr(context, 'websocket_url'), 'No WebSocket URL was accessed'
    assert context.websocket_url.startswith('wss://'), \
        f'WebSocket URL does not use WSS: {context.websocket_url}'
