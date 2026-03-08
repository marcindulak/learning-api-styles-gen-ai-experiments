@status-done
Feature: 011 API Documentation
  As a weather service developer
  I want to access API documentation
  So that I can understand how to use the APIs

  Scenario: OpenAPI schema is available
    When I send a GET request to "/api/schema/?format=json"
    Then the response status code is 200
    And the Content-Type is "application/vnd.oai.openapi"
    And the schema contains API version information
    And the schema contains endpoint paths

  Scenario: Swagger UI is accessible
    When I navigate to "/api/docs/" without authentication
    Then the response status code is 200
    And the page contains "Weather Forecast Service API"
    And the page contains API endpoints list

  Scenario: GraphQL playground is accessible
    When I navigate to "/graphql" without authentication
    Then the response status code is 200
    And the Content-Type is "text/html" for HTML requests

  Scenario: AsyncAPI documentation for WebSocket
    When I send a GET request to "/api/asyncapi/"
    Then the response status code is 200
    And the Content-Type is "application/json"
    And the schema documents WebSocket channels
