@status-todo
Feature: 003 - Weather Forecast

  As a user of the Weather Forecast Service
  I want to get weather forecasts for cities
  So that I can plan activities based on upcoming weather

  Background:
    Given the Weather Forecast Service is running
    And a city "Tokyo" exists in the system

  Scenario: Get weather forecast for a city
    When I request the weather forecast for city "Tokyo"
    Then I receive a response with status code 200
    And the response contains forecast data

  Scenario: Weather forecast is limited to 7 days maximum
    When I request the weather forecast for city "Tokyo" for 7 days
    Then I receive a response with status code 200
    And the response contains at most 7 days of forecast data

  Scenario: Reject forecast request exceeding 7 days
    When I request the weather forecast for city "Tokyo" for 10 days
    Then I receive a response with status code 400
    And the response contains error message about forecast limit

  Scenario: Forecast contains common weather indicators
    When I request the weather forecast for city "Tokyo"
    Then I receive a response with status code 200
    And the forecast contains temperature data
    And the forecast contains humidity data
    And the forecast contains wind speed data
    And the forecast contains weather condition description
