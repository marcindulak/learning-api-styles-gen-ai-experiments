from behave import then


@then("the connection was established using TLS")
def step_then_connection_used_tls(context):
    assert context.last_response.tls_version is not None, "connection did not use TLS"
