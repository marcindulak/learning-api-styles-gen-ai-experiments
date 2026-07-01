@status-todo
Feature: NFR-005 Service APIs are documented
  The HTTP APIs are documented with an OpenAPI specification and the
  WebSocket API is documented with an AsyncAPI specification. Both
  specifications are served by the running service.

  Scenario: OpenAPI specification is served
    Given the service is running
    When a client sends a GET request to "/api/schema"
    Then the response status code is 200
    And the response body is a YAML or JSON document containing the key "openapi" with a value starting with "3."
    And the document defines the path "/api/cities"
    And the document defines the path "/api/cities/{uuid}"

  Scenario: Interactive API documentation is served
    Given the service is running
    When a client sends a GET request to "/api/docs"
    Then the response status code is 200
    And the response content type is "text/html"

  Scenario: AsyncAPI specification documents the WebSocket alerts API
    Given the service is running
    When a client sends a GET request to "/api/asyncapi"
    Then the response status code is 200
    And the response body is a YAML or JSON document containing the key "asyncapi"
    And the document defines a channel for "/ws/alerts"
