@status-done
Feature: 004 - Weather Historical Data

  As a user of the Weather Forecast Service
  I want to access historical weather data
  So that I can analyze past weather patterns

  Background:
    Given the Weather Forecast Service is running
    And I have obtained a JWT access token for user "admin"
    And a city "Tokyo" exists in the system

  Scenario: Retrieve historical weather data for a city
    Given historical weather data exists for city "Tokyo" on date "2024-01-15"
    When I request historical weather data for city "Tokyo" on date "2024-01-15"
    Then I receive a response with status code 200
    And the response contains weather data for date "2024-01-15"

  Scenario: Historical data contains common weather indicators
    Given historical weather data exists for city "Tokyo" on date "2024-01-15"
    When I request historical weather data for city "Tokyo" on date "2024-01-15"
    Then I receive a response with status code 200
    And the historical data contains temperature
    And the historical data contains humidity
    And the historical data contains wind speed
    And the historical data contains weather condition

  Scenario: Return 404 for non-existent historical data
    When I request historical weather data for city "Tokyo" on date "1900-01-01"
    Then I receive a response with status code 404
