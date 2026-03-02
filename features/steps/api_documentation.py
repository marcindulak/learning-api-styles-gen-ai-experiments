"""Step definitions for API documentation feature."""

import subprocess

from behave import then, when


@when('I navigate to GraphQL endpoint "{endpoint}"')
def step_navigate_to_graphql(context, endpoint):
    """Navigate to GraphQL endpoint with proper Accept header."""
    result = subprocess.run(
        [
            'curl',
            '--header', 'Accept: text/html',
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


@then('the schema contains API version')
def step_schema_contains_version(context):
    """Verify the OpenAPI schema contains API version."""
    assert 'info' in context.response_json, \
        "Expected 'info' in schema"
    assert 'version' in context.response_json['info'], \
        "Expected 'version' in schema info"
    assert context.response_json['info']['version'], \
        "Version field is empty"


@then('the schema contains paths for "{path1}", "{path2}", "{path3}"')
def step_schema_contains_paths(context, path1, path2, path3):
    """Verify the OpenAPI schema contains specific paths."""
    assert 'paths' in context.response_json, \
        "Expected 'paths' in schema"

    paths = context.response_json['paths']
    for path in [path1, path2, path3]:
        found = False
        for schema_path in paths.keys():
            if path in schema_path:
                found = True
                break
        assert found, f"Expected path '{path}' in schema paths, got: {list(paths.keys())}"


@then('the page lists REST API endpoints')
def step_page_lists_rest_endpoints(context):
    """Verify the Swagger UI page lists REST API endpoints."""
    assert 'swagger' in context.response_body.lower() or 'api' in context.response_body.lower(), \
        "Expected Swagger UI content in page"


@then('the page contains GraphQL playground or documentation')
def step_page_contains_graphql_playground(context):
    """Verify the page contains GraphQL playground or documentation."""
    assert 'graphql' in context.response_body.lower() or 'graphiql' in context.response_body.lower(), \
        "Expected GraphQL playground or documentation in page"


@then('I can view the schema for queries "{query1}" and "{query2}"')
def step_view_graphql_schema(context, query1, query2):
    """Verify the GraphQL schema contains specific queries."""
    assert 'graphql' in context.response_body.lower() or 'graphiql' in context.response_body.lower(), \
        "Expected GraphQL interface in page"


@then('the schema documents WebSocket channel "{channel}"')
def step_schema_documents_websocket_channel(context, channel):
    """Verify the AsyncAPI schema documents a specific WebSocket channel."""
    assert 'channels' in context.response_json, \
        "Expected 'channels' in AsyncAPI schema"
    assert channel in context.response_json['channels'], \
        f"Expected channel '{channel}' in schema channels, got: {list(context.response_json['channels'].keys())}"


@then('the schema describes alert message format')
def step_schema_describes_alert_format(context):
    """Verify the AsyncAPI schema describes alert message format."""
    assert 'components' in context.response_json, \
        "Expected 'components' in AsyncAPI schema"
    assert 'messages' in context.response_json['components'], \
        "Expected 'messages' in schema components"
    assert 'schemas' in context.response_json['components'], \
        "Expected 'schemas' in schema components"
