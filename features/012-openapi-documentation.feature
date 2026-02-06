@status-todo
Feature: 012 API Documentation
  Service APIs are documented using OpenAPI specification
  allowing developers to understand and consume the APIs

  Scenario: OpenAPI specification is available
    Given the service is running
    When requesting OpenAPI schema from "/api/schema"
    Then a valid OpenAPI 3.0 specification is returned

  Scenario: OpenAPI spec documents REST endpoints
    Given the service is running
    When requesting OpenAPI schema from "/api/schema"
    Then the schema includes "/api/cities" endpoint
    And the schema documents GET, POST, PUT, PATCH, DELETE methods
    And each endpoint includes request and response schemas

  Scenario: Swagger UI is available for API exploration
    Given the service is running
    When navigating to "/api/docs"
    Then the Swagger UI interface is displayed
    And the UI shows all available endpoints

  Scenario: API documentation includes authentication requirements
    Given the service is running
    When requesting OpenAPI schema from "/api/schema"
    Then the schema includes security schemes
    And JWT authentication is documented
