@status-done
Feature: 004 REST API Weather Indicators
  As an API consumer
  I want to access current weather indicators via REST API
  So that I can integrate weather data into my applications

  Scenario: Current weather data is accessible via REST API
    Given a city "Copenhagen" exists
    And current weather data exists for Copenhagen
    When I request current weather for Copenhagen via REST
    Then the response includes temperature, humidity, wind_speed, pressure, and description
    And the response status is 200 OK

  Scenario: Weather data is returned as JSON
    Given a city "Copenhagen" exists
    And current weather data exists for Copenhagen
    When I request current weather for Copenhagen via REST
    Then the response is valid JSON
    And the response contains city metadata

  Scenario: REST API returns 404 for non-existent city
    Given no city named "NonExistent" exists
    When I request current weather for "NonExistent" via REST
    Then the response status is 404 Not Found

  Scenario: Authenticated users can access REST weather endpoints
    Given I am authenticated as a regular user
    And a city "Copenhagen" exists with weather data
    When I request current weather for Copenhagen via REST with authentication
    Then the request succeeds with status 200

  Scenario: Unauthenticated requests to weather endpoints are rejected
    Given no JWT token is provided
    When I request current weather for a city via REST
    Then the request fails with a 401 Unauthorized status
