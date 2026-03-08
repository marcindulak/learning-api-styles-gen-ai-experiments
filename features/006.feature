@status-done
Feature: 006 Third Party Weather API Integration
  As a weather service operator
  I want to fetch real weather data from a third-party API
  So that the service provides actual weather information

  Scenario: Fetch current weather from third-party API
    Given I am authenticated as admin
    And a city exists with name "London"
    And the third-party weather API is available
    When I trigger a fetch for current weather for "London"
    Then the response status code is 200
    And current weather data for "London" is stored

  Scenario: Fetch forecast from third-party API
    Given I am authenticated as admin
    And a city exists with name "Paris"
    And the third-party weather API is available
    When I trigger a fetch for forecast for "Paris"
    Then the response status code is 200
    And forecast data for "Paris" is stored

  Scenario: Handle third-party API unavailability
    Given I am authenticated as admin
    And a city exists with name "Berlin"
    And the third-party weather API is unavailable
    When I trigger a fetch for current weather for "Berlin"
    Then the response status code is 503
    And an error message is returned

  Scenario: Only admin can trigger third-party API fetch
    Given I am authenticated as regular user
    And a city exists with name "Tokyo"
    When I trigger a fetch for current weather for "Tokyo"
    Then the response status code is 403
