@status-todo
Feature: 013 Third-Party Weather API Integration
  Weather records contain actual data from a third-party weather API
  The service fetches real weather data from external sources

  Scenario: Fetch current weather from third-party API
    Given the service is running
    And a third-party weather API is configured
    And a city "Tokyo" exists with coordinates 35.6762, 139.6503
    When requesting current weather data for "Tokyo"
    Then the service fetches data from the third-party API
    And the weather data is stored in the system

  Scenario: Handle third-party API errors gracefully
    Given the service is running
    And a third-party weather API is configured
    And the third-party API is unavailable
    When requesting current weather data for "Delhi"
    Then the service returns a cached weather record or an error indicating API unavailability

  Scenario: Update weather data periodically
    Given the service is running
    And a third-party weather API is configured
    And a city "Shanghai" exists
    When the scheduled weather update task runs
    Then current weather data is fetched for all cities
    And the database is updated with new weather records

  Scenario: Respect third-party API rate limits
    Given the service is running
    And a third-party weather API is configured with rate limit 60 requests per minute
    When the service makes multiple weather data requests
    Then the service does not exceed 60 requests per minute
    And excess requests are queued for later processing
