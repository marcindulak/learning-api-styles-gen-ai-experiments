"""
Step definitions for OpenAPI documentation scenarios.
"""
import json

import yaml
from behave import given, then, when
from django.test import Client


@when('requesting OpenAPI schema from "{endpoint}"')
def request_openapi_schema(context, endpoint: str) -> None:
    """Request OpenAPI schema from specified endpoint."""
    client = Client()
    # Request JSON format explicitly
    response = client.get(endpoint, HTTP_ACCEPT="application/json")
    context.response = response
    if response.status_code == 200:
        content = response.content.decode("utf-8")
        # Try parsing as JSON, fall back to YAML if needed
        try:
            context.schema = json.loads(content)
        except json.JSONDecodeError:
            context.schema = yaml.safe_load(content)


@then("a valid OpenAPI 3.0 specification is returned")
def verify_valid_openapi_spec(context) -> None:
    """Verify that response contains valid OpenAPI 3.0 specification."""
    assert context.response.status_code == 200
    assert "openapi" in context.schema
    # OpenAPI 3.0.x or 3.1.x
    assert context.schema["openapi"].startswith("3.")
    assert "info" in context.schema
    assert "paths" in context.schema


@then('the schema includes "{endpoint}" endpoint')
def verify_endpoint_in_schema(context, endpoint: str) -> None:
    """Verify that schema includes specified endpoint."""
    assert "paths" in context.schema
    assert endpoint in context.schema["paths"]


@then("the schema documents GET, POST, PUT, PATCH, DELETE methods")
def verify_http_methods_documented(context) -> None:
    """Verify that schema documents standard HTTP methods for cities endpoint."""
    cities_endpoint = context.schema["paths"]["/api/cities"]
    assert "get" in cities_endpoint
    assert "post" in cities_endpoint

    # ViewSet detail routes use {uuid} or {id} parameter
    detail_endpoint_patterns = [
        path
        for path in context.schema["paths"].keys()
        if "/api/cities/{" in path and "}" in path
    ]
    assert len(detail_endpoint_patterns) > 0
    detail_endpoint = context.schema["paths"][detail_endpoint_patterns[0]]
    assert "get" in detail_endpoint
    assert "put" in detail_endpoint
    assert "patch" in detail_endpoint
    assert "delete" in detail_endpoint


@then("each endpoint includes request and response schemas")
def verify_request_response_schemas(context) -> None:
    """Verify that endpoints include request and response schemas."""
    cities_endpoint = context.schema["paths"]["/api/cities"]

    # GET should have responses
    assert "responses" in cities_endpoint["get"]

    # POST should have request body and responses
    assert "requestBody" in cities_endpoint["post"]
    assert "responses" in cities_endpoint["post"]


@when('navigating to "{endpoint}"')
def navigate_to_endpoint(context, endpoint: str) -> None:
    """Navigate to specified endpoint."""
    client = Client()
    response = client.get(endpoint)
    context.response = response


@then("the Swagger UI interface is displayed")
def verify_swagger_ui_displayed(context) -> None:
    """Verify that Swagger UI interface is displayed."""
    assert context.response.status_code == 200
    # Swagger UI returns HTML content
    assert "text/html" in context.response["Content-Type"]
    content = context.response.content.decode("utf-8")
    # Check for Swagger UI indicators in HTML
    assert "swagger-ui" in content.lower()


@then("the UI shows all available endpoints")
def verify_ui_shows_endpoints(context) -> None:
    """Verify that UI shows all available endpoints."""
    content = context.response.content.decode("utf-8")
    # Swagger UI uses the schema URL to load endpoints
    assert "api/schema" in content


@then("the schema includes security schemes")
def verify_security_schemes(context) -> None:
    """Verify that schema includes security schemes."""
    assert "components" in context.schema
    assert "securitySchemes" in context.schema["components"]


@then("JWT authentication is documented")
def verify_jwt_authentication_documented(context) -> None:
    """Verify that JWT authentication is documented in schema."""
    security_schemes = context.schema["components"]["securitySchemes"]
    # drf-spectacular uses "jwtAuth" as the security scheme name by default
    jwt_scheme = None
    for scheme_name, scheme_config in security_schemes.items():
        if scheme_config.get("type") == "http" and scheme_config.get("scheme") == "bearer":
            jwt_scheme = scheme_config
            break
    assert jwt_scheme is not None
    assert jwt_scheme["bearerFormat"] == "JWT"
