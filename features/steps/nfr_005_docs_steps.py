from behave import then
from common_steps import _response_body

# The OpenAPI/AsyncAPI "valid document" step pair below is near-identical
# WET, not left un-deduplicated by oversight: CLAUDE.md permits WET over a
# hasty abstraction, and the two documents assert different key names
# ("openapi"/"paths" vs. "asyncapi"/"channels"), so a parametrized version
# would trade two clear 4-line steps for one step with two indirected lookups.


@then("the response body is a valid OpenAPI document")
def step_then_valid_openapi_document(context):
    body = _response_body(context)
    assert body["openapi"].startswith("3.")
    assert "paths" in body


@then('the document describes the "{path}" path')
def step_then_openapi_describes_path(context, path):
    assert path in _response_body(context)["paths"]


@then("the response body is a valid AsyncAPI document")
def step_then_valid_asyncapi_document(context):
    body = _response_body(context)
    assert body["asyncapi"].startswith("3.")
    assert "channels" in body


@then("the document describes the WebSocket alerts channel and the GitHub webhook channel")
def step_then_asyncapi_describes_channels(context):
    addresses = [channel["address"] for channel in _response_body(context)["channels"].values()]
    assert any("/ws/alerts/" in address for address in addresses)
    assert "/api/webhooks/github" in addresses
