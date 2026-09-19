@status-done
Feature: FR-009 - Weather forecast limited to 7 days
  A forecast request accepts a number of days between 1 and 7 inclusive.
  Requests outside that range are rejected.

  Background:
    Given the city "Mexico City" exists with uuid "44444444-4444-4444-4444-444444444444"
    And "Mexico City" has a 7-day forecast with one entry per day

  Scenario: Requesting the maximum allowed forecast length
    When a client sends "GET /api/cities/44444444-4444-4444-4444-444444444444/forecast?days=7"
    Then the response status is 200
    And the response body contains 7 forecast entries

  Scenario: Requesting a forecast beyond 7 days is rejected
    When a client sends "GET /api/cities/44444444-4444-4444-4444-444444444444/forecast?days=10"
    Then the response status is 400
    And the response body contains an error message stating the maximum is 7 days

  Scenario: Requesting a forecast of 0 days is rejected
    When a client sends "GET /api/cities/44444444-4444-4444-4444-444444444444/forecast?days=0"
    Then the response status is 400
