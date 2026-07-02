"""Steps for the API documentation endpoints (OpenAPI, AsyncAPI).

The specification documents may be served as YAML or JSON; YAML is a
superset of JSON, so yaml.safe_load parses both. The parsed document is
cached on the context so follow-up assertions of the same scenario reuse
it.
"""
import parse
import yaml
from behave import register_type, then


@parse.with_pattern(r'[^"]*')
def parse_quoted(text):
    return text


register_type(Q=parse_quoted)


def parsed_document(context):
    if not hasattr(context, "spec_document"):
        document = yaml.safe_load(context.response.text)
        assert isinstance(document, dict), (
            f"response body is not a YAML/JSON mapping: {context.response.text[:200]}"
        )
        context.spec_document = document
    return context.spec_document


@then(
    'the response body is a YAML or JSON document containing the key "{key:Q}" '
    'with a value starting with "{prefix:Q}"'
)
def step_document_key_with_prefix(context, key, prefix):
    document = parsed_document(context)
    assert key in document, f'key "{key}" not in document: {list(document)}'
    value = str(document[key])
    assert value.startswith(prefix), (
        f'expected "{key}" to start with "{prefix}", got "{value}"'
    )


@then('the response body is a YAML or JSON document containing the key "{key:Q}"')
def step_document_key(context, key):
    document = parsed_document(context)
    assert key in document, f'key "{key}" not in document: {list(document)}'


@then('the document defines the path "{path:Q}"')
def step_document_defines_path(context, path):
    paths = parsed_document(context).get("paths", {})
    assert path in paths, f'path "{path}" not in documented paths: {list(paths)}'


@then('the document defines a channel for "{address:Q}"')
def step_document_defines_channel(context, address):
    channels = parsed_document(context).get("channels", {})
    # AsyncAPI 3.x channels carry the path in "address"; in AsyncAPI 2.x
    # the channel key itself is the path. Accept either form.
    matches = address in channels or any(
        isinstance(channel, dict) and channel.get("address") == address
        for channel in channels.values()
    )
    assert matches, f'no channel for "{address}" in channels: {channels}'
