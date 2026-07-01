@status-todo
Feature: FR-001 Service exposes common weather indicators via various web APIs
  The service exposes common weather indicators (temperature, humidity,
  wind speed, pressure, precipitation) for a city through both a REST API
  and a GraphQL API.

  Scenario: REST API returns current weather indicators for a city
    Given the service is running
    And a city named "Tokyo" exists
    And a weather record for "Tokyo" exists with temperature 21.5, humidity 60, wind_speed 5.2, pressure 1013, precipitation 0.0
    When a client sends a GET request to "/api/cities/<city_uuid>/weather" for the city "Tokyo"
    Then the response status code is 200
    And the response content type is "application/json"
    And the response JSON contains the field "temperature" with value 21.5
    And the response JSON contains the field "humidity" with value 60
    And the response JSON contains the field "wind_speed" with value 5.2
    And the response JSON contains the field "pressure" with value 1013
    And the response JSON contains the field "precipitation" with value 0.0

  Scenario: REST API lists cities
    Given the service is running
    And a city named "Tokyo" exists
    When a client sends a GET request to "/api/cities?search_name=Tokyo"
    Then the response status code is 200
    And the response JSON field "results" contains an entry with "name" equal to "Tokyo"
    And that entry contains a non-empty "uuid" field

  Scenario: GraphQL API returns current weather indicators for a city
    Given the service is running
    And a city named "Tokyo" exists
    And a weather record for "Tokyo" exists with temperature 21.5, humidity 60, wind_speed 5.2, pressure 1013, precipitation 0.0
    When a client sends a GraphQL query for the current weather of "Tokyo" to "/graphql" requesting fields "temperature humidity windSpeed pressure precipitation"
    Then the response status code is 200
    And the response JSON path "data.weather.temperature" equals 21.5
    And the response JSON path "data.weather.humidity" equals 60
    And the response JSON path "data.weather.windSpeed" equals 5.2
    And the response JSON path "data.weather.pressure" equals 1013
    And the response JSON path "data.weather.precipitation" equals 0.0

  Scenario: REST API returns 404 for a non-existing city
    Given the service is running
    When a client sends a GET request to "/api/cities/00000000-0000-0000-0000-000000000000"
    Then the response status code is 404
