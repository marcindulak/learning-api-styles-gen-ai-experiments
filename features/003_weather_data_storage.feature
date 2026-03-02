@status-done
Feature: 003 Weather Data Storage
  The Weather Forecast Service stores historical weather data and forecasts.
  Weather records contain common weather indicators: temperature, humidity, pressure, wind speed, and conditions.

  Scenario: Store current weather data for a city
    Given the service is running
    And I am authenticated as admin
    And a city "Copenhagen" exists
    When I send a POST request to "/api/weather/current" with data:
      | city_name     | Copenhagen  |
      | temperature   | 15.5        |
      | humidity      | 65          |
      | pressure      | 1013        |
      | wind_speed    | 12.3        |
      | conditions    | Partly Cloudy|
      | timestamp     | 2024-01-15T12:00:00Z |
    Then the response status code is 201
    And the response contains field "city_name" with value "Copenhagen"
    And the response contains field "temperature" with value 15.5

  Scenario: Retrieve historical weather data for a city
    Given the service is running
    And a city "Copenhagen" exists
    And weather data exists for "Copenhagen" on "2024-01-15T12:00:00Z"
    When I send a GET request to "/api/weather/historical?city=Copenhagen&start_date=2024-01-15&end_date=2024-01-16"
    Then the response status code is 200
    And the response contains a list with at least 1 items

  Scenario: Store forecast data with 7-day limit
    Given the service is running
    And I am authenticated as admin
    And a city "Copenhagen" exists
    When I send a POST request to "/api/weather/forecast" with data:
      | city_name   | Copenhagen  |
      | forecast_date | 2024-01-20 |
      | temperature | 12.0        |
      | humidity    | 70          |
      | pressure    | 1010        |
      | wind_speed  | 8.5         |
      | conditions  | Rainy       |
    Then the response status code is 201
    And the response contains field "forecast_date" with value "2024-01-20"

  Scenario: Reject forecast data beyond 7 days
    Given the service is running
    And I am authenticated as admin
    And a city "Copenhagen" exists
    When I send a POST request to "/api/weather/forecast" with data:
      | city_name   | Copenhagen  |
      | forecast_date | 2026-03-10 |
      | temperature | 10.0        |
      | humidity    | 75          |
      | pressure    | 1008        |
      | wind_speed  | 10.0        |
      | conditions  | Cloudy      |
    Then the response status code is 400
    And the response contains an error message about forecast limit
