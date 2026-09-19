@status-done
Feature: NFR-005 - Service APIs are documented
  The synchronous APIs are documented with an OpenAPI specification and
  the asynchronous APIs (WebSocket alerts, GitHub webhook) are
  documented with an AsyncAPI specification.

  Scenario: OpenAPI specification is available and valid
    When a client sends "GET /api/schema"
    Then the response status is 200
    And the response body is a valid OpenAPI document
    And the document describes the "/api/cities" path

  Scenario: AsyncAPI specification is available and valid
    When a client sends "GET /api/async-schema"
    Then the response status is 200
    And the response body is a valid AsyncAPI document
    And the document describes the WebSocket alerts channel and the GitHub webhook channel
