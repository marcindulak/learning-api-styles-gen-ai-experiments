@status-todo
Feature: FR-005 Service provides weather historical data
  The service stores weather records with observation timestamps and lets
  clients query historical weather data of a city for a given time range.

  Scenario: Historical weather data for a date range is returned
    Given the service is running
    And a city named "Tokyo" exists
    And weather records for "Tokyo" exist for each day from "2026-06-01" to "2026-06-10"
    When a client sends a GET request to "/api/cities/<city_uuid>/weather/history?start=2026-06-03&end=2026-06-05" for the city "Tokyo"
    Then the response status code is 200
    And the response JSON field "results" contains exactly 3 records
    And every record has an "observed_at" timestamp between "2026-06-03T00:00:00Z" and "2026-06-05T23:59:59Z"
    And the records are ordered by "observed_at" ascending

  Scenario: Historical query outside the stored range returns an empty result
    Given the service is running
    And a city named "Tokyo" exists
    And weather records for "Tokyo" exist for each day from "2026-06-01" to "2026-06-10"
    When a client sends a GET request to "/api/cities/<city_uuid>/weather/history?start=2020-01-01&end=2020-01-31" for the city "Tokyo"
    Then the response status code is 200
    And the response JSON field "results" contains exactly 0 records

  Scenario: Historical query with an invalid date range returns an error
    Given the service is running
    And a city named "Tokyo" exists
    When a client sends a GET request to "/api/cities/<city_uuid>/weather/history?start=2026-06-10&end=2026-06-01" for the city "Tokyo"
    Then the response status code is 400
