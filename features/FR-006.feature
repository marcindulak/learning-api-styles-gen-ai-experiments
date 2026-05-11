@status-done
Feature: FR-006 Weather historical data

  The service stores past weather observations and exposes them through a REST
  endpoint.

  Scenario: Retrieve a stored historical record by date
    Given the service is running
    And a city named "Tokyo" exists
    And a weather record for "Tokyo" on "2025-01-15" with temperature 5.0 exists
    When a client sends GET to "/api/cities/Tokyo/weather/history?date=2025-01-15"
    Then the response status is 200
    And the response body has a key "results[0].temperature" with the value 5.0
    And the response body has a key "results[0].observed_on" with the value "2025-01-15"

  Scenario: Request historical data for a date without records
    Given the service is running
    And a city named "Tokyo" exists
    When a client sends GET to "/api/cities/Tokyo/weather/history?date=1900-01-01"
    Then the response status is 200
    And the response body has a key "results" with an empty list
