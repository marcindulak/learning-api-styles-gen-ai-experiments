@status-done
Feature: FR-009 Weather forecast is limited to up to 7 days
  The service provides weather forecasts covering at most 7 days ahead.
  Forecast queries never return entries further than 7 days in the future.

  Scenario: Forecast returns at most 7 daily entries
    Given the service is running
    And a city named "Tokyo" exists
    And forecast records for "Tokyo" exist for the next 7 days
    When a client sends a GET request to "/api/cities/<city_uuid>/forecast" for the city "Tokyo"
    Then the response status code is 200
    And the response JSON field "results" contains exactly 7 records
    And every record has a "forecast_date" within 7 days from today

  Scenario: Requesting fewer days than available limits the result
    Given the service is running
    And a city named "Tokyo" exists
    And forecast records for "Tokyo" exist for the next 7 days
    When a client sends a GET request to "/api/cities/<city_uuid>/forecast?days=3" for the city "Tokyo"
    Then the response status code is 200
    And the response JSON field "results" contains exactly 3 records

  Scenario: Requesting more than 7 days is rejected
    Given the service is running
    And a city named "Tokyo" exists
    When a client sends a GET request to "/api/cities/<city_uuid>/forecast?days=8" for the city "Tokyo"
    Then the response status code is 400
    And the response JSON contains an error message mentioning the maximum of 7 days

  Scenario: Forecast records beyond 7 days cannot be stored
    Given the service is running
    And a city named "Tokyo" exists
    When an attempt is made to store a forecast record for "Tokyo" with a forecast_date 8 days from today
    Then the forecast record is rejected with a validation error
    And "Tokyo" has 0 forecast records
