@status-done
Feature: NFR-005 Service APIs are documented

  The service publishes machine-readable specifications for its synchronous
  (OpenAPI) and asynchronous (AsyncAPI) APIs.

  Scenario: OpenAPI specification is served
    Given the service is running
    When a client sends GET to "/api/schema"
    Then the response status is 200
    And the response body contains the substring "openapi:"

  Scenario: Swagger UI is served
    Given the service is running
    When a client sends GET to "/api/docs"
    Then the response status is 200
    And the response Content-Type starts with "text/html"

  Scenario: AsyncAPI specification is served for the WebSocket API
    Given the service is running
    When a client sends GET to "/api/asyncapi"
    Then the response status is 200
    And the response body contains the substring "asyncapi:"
