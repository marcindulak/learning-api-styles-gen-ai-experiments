@status-todo
Feature: 013 Third-Party Weather API Integration
  As a system
  I need to integrate with a third-party weather API
  So that I can fetch actual weather data

  Scenario: Fetch current weather from third-party API
    Given a third-party weather API is configured and available
    And a city "Copenhagen" exists in the system
    When the system fetches current weather for "Copenhagen"
    Then the third-party API is called with the city coordinates
    And the response contains temperature, humidity, pressure, and wind speed
    And the data is stored in the local database

  Scenario: Fallback to cached data if third-party API is unavailable
    Given a third-party weather API is configured but unavailable
    And cached weather data exists for "Copenhagen"
    When the system attempts to fetch current weather for "Copenhagen"
    Then the system returns the cached data
    And a warning is logged about the API unavailability
