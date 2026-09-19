@status-done
Feature: FR-001 - Weather indicators via REST and GraphQL APIs
  The service exposes current weather indicators (temperature, humidity,
  wind speed, precipitation probability, condition) for a city through
  both a REST API and a GraphQL API.

  Background:
    Given the city "Tokyo" exists with uuid "11111111-1111-1111-1111-111111111111"
    And "Tokyo" has a current weather record with temperature 22.5, humidity 60, wind_speed 12.0, precipitation_probability 10, and condition "Clear"

  Scenario: Retrieve current weather indicators via REST API
    When a client sends "GET /api/cities/11111111-1111-1111-1111-111111111111/current"
    Then the response status is 200
    And the response body contains "temperature" equal to 22.5
    And the response body contains "humidity" equal to 60
    And the response body contains "wind_speed" equal to 12.0
    And the response body contains "precipitation_probability" equal to 10
    And the response body contains "condition" equal to "Clear"

  Scenario: Retrieve current weather indicators via GraphQL API
    When a client sends a "POST /api/graphql" query requesting temperature, humidity, windSpeed, precipitationProbability, and condition for city uuid "11111111-1111-1111-1111-111111111111"
    Then the response status is 200
    And the GraphQL response field "currentWeather.temperature" equals 22.5
    And the GraphQL response field "currentWeather.condition" equals "Clear"

  Scenario: REST API returns 404 for a city that does not exist
    When a client sends "GET /api/cities/99999999-9999-9999-9999-999999999999/current"
    Then the response status is 404

  Scenario: GraphQL API returns an errors field for a city that does not exist
    When a client sends a "POST /api/graphql" query requesting temperature for city uuid "99999999-9999-9999-9999-999999999999"
    Then the response status is 200
    And the GraphQL response contains an "errors" field
    And the GraphQL response field "currentWeather" is null
