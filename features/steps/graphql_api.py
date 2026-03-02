"""Step definitions for GraphQL API feature."""

import json
import subprocess

from behave import then, when


@when('I send a GraphQL query')
def step_send_graphql_query(context):
    """Send a GraphQL query from the context text."""
    query = context.text.strip()
    payload = json.dumps({'query': query})

    result = subprocess.run(
        [
            'curl',
            '--data', payload,
            '--header', 'Content-Type: application/json',
            '--request', 'POST',
            '--silent',
            '--write-out', '\\n%{http_code}',
            'http://localhost:8000/graphql'
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


@then('the GraphQL response is successful')
def step_graphql_response_successful(context):
    """Verify that the GraphQL response is successful (200 status and no errors)."""
    assert context.response_status_code == 200, \
        f"Expected status code 200, got {context.response_status_code}"
    assert 'errors' not in context.response_json, \
        f"GraphQL errors found: {context.response_json.get('errors')}"
    assert 'data' in context.response_json, \
        f"No data field in response: {context.response_json}"




@then('the GraphQL response contains field "{field_path}" equals "{expected_value}"')
def step_graphql_response_contains_field_equals(context, field_path, expected_value):
    """Verify that a nested field equals an expected value in the GraphQL response."""
    data = context.response_json.get('data', {})
    keys = field_path.split('.')
    current = data

    for key in keys:
        if key not in current:
            raise AssertionError(f"Field '{key}' not found in {current}. Full path: {field_path}")
        current = current[key]

    assert str(current) == expected_value, \
        f"Expected '{expected_value}' at {field_path}, got '{current}'"


@then('the GraphQL response has field "{field_path}"')
def step_graphql_response_has_field(context, field_path):
    """Verify that a nested field exists in the GraphQL response."""
    data = context.response_json.get('data', {})
    keys = field_path.split('.')
    current = data

    for key in keys:
        if current is None:
            raise AssertionError(f"Cannot navigate to '{key}' because current value is None. Full path: {field_path}. Data: {data}")
        if key not in current:
            raise AssertionError(f"Field '{key}' not found in {current}. Full path: {field_path}")
        current = current[key]

    assert current is not None, f"Field at {field_path} is None"


@then('the GraphQL response does not contain field "{field_path}"')
def step_graphql_response_does_not_contain_field(context, field_path):
    """Verify that a nested field does not exist in the GraphQL response."""
    data = context.response_json.get('data', {})
    keys = field_path.split('.')
    current = data

    for key in keys:
        if key not in current:
            return
        current = current[key]
        if current is None:
            return

    raise AssertionError(f"Field {field_path} should not exist but was found: {current}")


@then('the GraphQL response contains a list "{list_name}" with {count:d} items')
def step_graphql_response_contains_list_with_count(context, list_name, count):
    """Verify that a list field contains the expected number of items in the GraphQL response."""
    data = context.response_json.get('data', {})
    assert list_name in data, \
        f"List '{list_name}' not found in response data: {data}"

    items = data[list_name]
    assert isinstance(items, list), \
        f"'{list_name}' is not a list: {items}"
    assert len(items) == count, \
        f"Expected {count} items in '{list_name}', got {len(items)}"
