"""
Step definitions for API Documentation feature.
"""
import json
import subprocess
from behave import when, then


@then('the schema contains API version information')
def step_schema_contains_version(context):
    """Verify OpenAPI schema contains version information."""
    response_data = json.loads(context.response_body)
    assert 'info' in response_data, "Schema missing 'info' field"
    assert 'version' in response_data['info'], "Schema missing version information"
    assert len(response_data['info']['version']) > 0, "Version information is empty"


@then('the schema contains endpoint paths')
def step_schema_contains_paths(context):
    """Verify OpenAPI schema contains endpoint paths."""
    response_data = json.loads(context.response_body)
    assert 'paths' in response_data, "Schema missing 'paths' field"
    assert len(response_data['paths']) > 0, "No endpoint paths found in schema"


@then('the page contains API endpoints list')
def step_page_contains_api_endpoints(context):
    """Verify Swagger UI page contains API endpoints list."""
    # Swagger UI should contain references to API endpoints or the schema
    assert '/api/' in context.response_body or 'swagger' in context.response_body.lower(), \
        "API endpoints list not found in Swagger UI page"


@when('I navigate to "{url}" without authentication')
def step_navigate_without_auth(context, url):
    """Navigate to a URL without authentication."""
    curl_command_code = [
        "curl",
        "--request", "GET",
        "--header", "Accept: text/html",
        "--silent",
        "--output", "/dev/null",
        "--write-out", "%{http_code}",
        f"http://localhost:8000{url}"
    ]
    result_code = subprocess.run(
        curl_command_code,
        capture_output=True,
        text=True
    )
    context.response_status_code = int(result_code.stdout)

    curl_command_body = [
        "curl",
        "--request", "GET",
        "--header", "Accept: text/html",
        "--silent",
        f"http://localhost:8000{url}"
    ]
    result_body = subprocess.run(
        curl_command_body,
        capture_output=True,
        text=True
    )
    context.response_body = result_body.stdout
    context.last_endpoint = url


@then('the Content-Type is "{content_type}" for HTML requests')
def step_content_type_for_html(context, content_type):
    """Verify Content-Type header for requests with Accept: text/html."""
    curl_command = [
        "curl",
        "--request", "GET",
        "--header", "Accept: text/html",
        "--silent",
        "--output", "/dev/null",
        "--write-out", "%{content_type}",
        f"http://localhost:8000{context.last_endpoint}"
    ]

    result = subprocess.run(
        curl_command,
        capture_output=True,
        text=True
    )
    actual_content_type = result.stdout.strip()
    assert content_type in actual_content_type, \
        f"Expected Content-Type to contain '{content_type}', but got '{actual_content_type}'"


@then('the schema documents WebSocket channels')
def step_schema_documents_websocket_channels(context):
    """Verify AsyncAPI schema documents WebSocket channels."""
    response_data = json.loads(context.response_body)
    assert 'channels' in response_data, "AsyncAPI schema missing 'channels' field"
    assert len(response_data['channels']) > 0, "No WebSocket channels documented in schema"
    # Verify the alerts channel is documented
    assert any('/ws/alerts/' in channel for channel in response_data['channels']), \
        "WebSocket alerts channel not found in AsyncAPI schema"
