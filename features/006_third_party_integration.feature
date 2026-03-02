@status-done
Feature: 006 Third Party Weather API Integration
  The Weather Forecast Service integrates with a third-party weather API to populate actual weather data.
  Data is fetched and stored for the configured cities.

  Scenario: Fetch current weather from third-party API
    Given the service is running
    And I am authenticated as admin
    And a city "Copenhagen" exists
    And the third-party weather API is available
    When I send a POST request to "/api/admin/fetch-weather" with data:
      | city_name | Copenhagen |
      | data_type | current    |
    Then the response status code is 200
    And weather data for "Copenhagen" is stored in the database

  Scenario: Fetch forecast from third-party API
    Given the service is running
    And I am authenticated as admin
    And a city "Copenhagen" exists
    And the third-party weather API is available
    When I send a POST request to "/api/admin/fetch-weather" with data:
      | city_name | Copenhagen |
      | data_type | forecast   |
    Then the response status code is 200
    And forecast data for "Copenhagen" is stored in the database

  Scenario: Handle third-party API failure gracefully
    Given the service is running
    And I am authenticated as admin
    And a city "Copenhagen" exists
    And the third-party weather API is unavailable
    When I send a POST request to "/api/admin/fetch-weather" with data:
      | city_name | Copenhagen |
      | data_type | current    |
    Then the response status code is 503
    And the response contains an error message about API unavailability

  Scenario: Only admin can trigger data fetch
    Given the service is running
    And I am authenticated as a regular user
    And a city "Copenhagen" exists
    When I send a POST request to "/api/admin/fetch-weather" with data:
      | city_name | Copenhagen |
      | data_type | current    |
    Then the response status code is 403
