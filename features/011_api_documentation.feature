@status-todo
Feature: 011 API Documentation
  The Weather Forecast Service APIs are documented using OpenAPI and AsyncAPI specifications.
  Documentation is accessible to developers integrating with the service.

  Scenario: Access OpenAPI specification for REST API
    Given the service is running
    When I send a GET request to "/api/schema/"
    Then the response status code is 200
    And the response Content-Type is "application/vnd.oai.openapi+json"
    And the schema contains API version
    And the schema contains paths for "/api/cities", "/api/weather/current", "/api/weather/forecast"

  Scenario: Access Swagger UI for REST API
    Given the service is running
    When I navigate to "/api/docs/"
    Then the response status code is 200
    And the page contains "Swagger UI"
    And the page lists REST API endpoints

  Scenario: Access GraphQL schema documentation
    Given the service is running
    When I navigate to "/graphql/"
    Then the response status code is 200
    And the page contains GraphQL playground or documentation
    And I can view the schema for queries "currentWeather" and "forecast"

  Scenario: Access AsyncAPI specification for WebSocket
    Given the service is running
    When I send a GET request to "/api/asyncapi-schema/"
    Then the response status code is 200
    And the response Content-Type is "application/json"
    And the schema documents WebSocket channel "/ws/alerts"
    And the schema describes alert message format
