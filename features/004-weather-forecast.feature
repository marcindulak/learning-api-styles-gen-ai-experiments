@status-todo
Feature: 004 Weather Forecast
  Weather forecast is limited to up to 7 days
  The service provides weather forecast data for cities

  Scenario: Forecast is limited to maximum 7 days
    Given the service is running
    And a city "Tokyo" exists
    When requesting a weather forecast for "Tokyo" for 7 days
    Then a forecast for exactly 7 days is returned

  Scenario: Cannot request forecast beyond 7 days
    Given the service is running
    And a city "Delhi" exists
    When requesting a weather forecast for "Delhi" for 10 days
    Then an error response is returned indicating maximum 7 days

  Scenario: Forecast contains weather indicators for each day
    Given the service is running
    And a city "Shanghai" exists
    When requesting a weather forecast for "Shanghai" for 3 days
    Then the forecast contains 3 daily predictions
    And each prediction includes temperature, humidity, and pressure
