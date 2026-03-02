@status-done
Feature: 004 REST API for Weather Data
  The Weather Forecast Service exposes common weather indicators via REST API.
  The API provides access to current weather, forecasts, and historical data.

  Scenario: Get current weather for a city
    Given the service is running
    And a city "Copenhagen" exists
    And current weather data exists for "Copenhagen"
    When I send a GET request to "/api/weather/current/Copenhagen"
    Then the response status code is 200
    And the response contains field "city_name" with value "Copenhagen"
    And the response contains field "temperature"
    And the response contains field "humidity"
    And the response contains field "pressure"
    And the response contains field "wind_speed"
    And the response contains field "conditions"

  Scenario: Get 7-day forecast for a city
    Given the service is running
    And a city "Copenhagen" exists
    And forecast data exists for "Copenhagen" for the next 7 days
    When I send a GET request to "/api/weather/forecast/Copenhagen"
    Then the response status code is 200
    And the response contains a list with 7 items
    And each forecast contains fields "forecast_date", "temperature", "humidity", "pressure", "wind_speed", "conditions"

  Scenario: Get weather data for non-existent city
    Given the service is running
    When I send a GET request to "/api/weather/current/NonExistentCity"
    Then the response status code is 404

  Scenario: List all cities with current weather
    Given the service is running
    And cities "Copenhagen", "Tokyo", "New York" exist
    And current weather data exists for all cities
    When I send a GET request to "/api/weather/current"
    Then the response status code is 200
    And the response contains a list with 3 items
