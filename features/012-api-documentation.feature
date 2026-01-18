@status-todo
Feature: 012 API Documentation
  As a client developer
  I need API documentation
  So that I can understand how to use the service APIs

  Scenario: OpenAPI specification is available for REST API
    Given the service has REST endpoints
    When a client requests the OpenAPI specification
    Then an OpenAPI 3.0 specification is returned
    And the specification documents all REST endpoints
    And each endpoint includes request/response schemas

  Scenario: AsyncAPI specification is available for WebSocket API
    Given the service has WebSocket endpoints
    When a client requests the AsyncAPI specification
    Then an AsyncAPI specification is returned
    And the specification documents the WebSocket message schema
    And the specification includes example payloads
