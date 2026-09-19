@status-done
Feature: FR-005 - Weather historical data
  The service stores past weather records for a city and exposes them
  through a date-range query.

  Background:
    Given the city "Shanghai" exists with uuid "55555555-5555-5555-5555-555555555555"
    And "Shanghai" has historical weather records for every day from "2026-01-01" to "2026-01-10"

  Scenario: Retrieve historical weather data for a valid date range
    When a client sends "GET /api/cities/55555555-5555-5555-5555-555555555555/history?start=2026-01-02&end=2026-01-05"
    Then the response status is 200
    And the response body contains 4 records
    And the records are ordered by date ascending

  Scenario: Historical data request with start date after end date returns an error
    When a client sends "GET /api/cities/55555555-5555-5555-5555-555555555555/history?start=2026-01-05&end=2026-01-02"
    Then the response status is 400

  Scenario: Historical data request for a range before the city was added returns an empty result
    When a client sends "GET /api/cities/55555555-5555-5555-5555-555555555555/history?start=2025-01-01&end=2025-01-05"
    Then the response status is 200
    And the response body contains 0 records

  Scenario: Historical data request for a nonexistent city returns not found
    When a client sends "GET /api/cities/99999999-9999-9999-9999-999999999999/history?start=2026-01-02&end=2026-01-05"
    Then the response status is 404
