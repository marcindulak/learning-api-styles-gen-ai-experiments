import subprocess

from behave import given, then, when


@when('sending an HTTP request to "{url}"')
def step_send_http_request(context, url: str):
    """Send an HTTP request to the service."""
    result = subprocess.run(
        ["curl", "--request", "GET", "--silent", "--output", "/dev/null", "--write-out", "%{http_code}", url],
        capture_output=True,
        text=True,
    )
    context.response_code = result.stdout.strip()
    context.request_success = result.returncode == 0


@then("the request is processed successfully")
def step_verify_request_processed(context):
    """Verify the request was processed successfully."""
    assert context.request_success, "Request failed"
    assert context.response_code in [
        "200",
        "301",
        "302",
        "404",
    ], f"Expected success status code, got {context.response_code}"


@given("the service is running with TLS enabled")
def step_service_running_with_tls(context):
    """Verify TLS is enabled in the service."""
    result = subprocess.run(
        ["sh", "-c", "echo $TLS_ENABLE"],
        capture_output=True,
        text=True,
    )
    tls_enable = result.stdout.strip()
    context.tls_enabled = tls_enable == "1"
    if not context.tls_enabled:
        context.scenario.skip("TLS is not enabled (TLS_ENABLE=0), skipping HTTPS test")


@when('sending an HTTPS request to "{url}"')
def step_send_https_request(context, url: str):
    """Send an HTTPS request to the service."""
    result = subprocess.run(
        [
            "curl",
            "--request",
            "GET",
            "--silent",
            "--insecure",
            "--output",
            "/dev/null",
            "--write-out",
            "%{http_code}",
            url,
        ],
        capture_output=True,
        text=True,
    )
    context.response_code = result.stdout.strip()
    context.request_success = result.returncode == 0


@then("the connection is encrypted")
def step_verify_connection_encrypted(context):
    """Verify the connection used encryption."""
    assert context.request_success, "HTTPS request failed"
    assert context.response_code in [
        "200",
        "301",
        "302",
        "404",
    ], f"Expected success status code, got {context.response_code}"


@given("the service is running without TLS")
def step_service_running_without_tls(context):
    """Verify TLS is disabled in the service."""
    result = subprocess.run(
        ["sh", "-c", "echo $TLS_ENABLE"],
        capture_output=True,
        text=True,
    )
    tls_enable = result.stdout.strip()
    context.tls_enabled = tls_enable == "1"
    assert not context.tls_enabled, "TLS should be disabled but is enabled"


@when("checking service configuration")
def step_check_service_configuration(context):
    """Check the service configuration for TLS settings."""
    result = subprocess.run(
        ["sh", "-c", "echo $TLS_ENABLE"],
        capture_output=True,
        text=True,
    )
    context.tls_enable_value = result.stdout.strip()


@then("HTTP endpoint is available")
def step_verify_http_endpoint_available(context):
    """Verify HTTP endpoint is available."""
    result = subprocess.run(
        [
            "curl",
            "--request",
            "GET",
            "--silent",
            "--output",
            "/dev/null",
            "--write-out",
            "%{http_code}",
            "http://localhost:8000/api/cities",
        ],
        capture_output=True,
        text=True,
    )
    http_available = result.returncode == 0 and result.stdout.strip() in [
        "200",
        "301",
        "302",
        "404",
    ]
    assert http_available, "HTTP endpoint should be available"


@then("HTTPS endpoint is not available")
def step_verify_https_endpoint_not_available(context):
    """Verify HTTPS endpoint is not available."""
    result = subprocess.run(
        [
            "curl",
            "--request",
            "GET",
            "--silent",
            "--insecure",
            "--max-time",
            "2",
            "--output",
            "/dev/null",
            "--write-out",
            "%{http_code}",
            "https://localhost:8443/api/cities",
        ],
        capture_output=True,
        text=True,
    )
    https_unavailable = result.returncode != 0 or result.stdout.strip() == "000"
    assert https_unavailable, "HTTPS endpoint should not be available when TLS is disabled"
