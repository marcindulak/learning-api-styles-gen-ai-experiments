@status-todo
Feature: 003 REST API for Weather Indicators
  As a client application
  I need to query weather indicators via REST API
  So that I can display current weather conditions

  Scenario: Retrieve current weather for a city
    Given a city "Copenhagen" exists in the system
    And weather data is available for "Copenhagen"
    When the client sends a GET request to /api/weather?city=Copenhagen
    Then the system returns HTTP 200 OK
    And the response contains weather indicators (temperature, humidity, pressure, wind speed)
    And the response is in JSON format

  Scenario: REST API returns error for non-existent city
    Given no city named "InvalidCity" exists in the system
    When the client sends a GET request to /api/weather?city=InvalidCity
    Then the system returns HTTP 404 Not Found
    And the response contains an error message
