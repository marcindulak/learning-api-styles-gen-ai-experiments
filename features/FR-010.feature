@status-done
Feature: FR-010 Forecast horizon limited to 7 days

  The service exposes a forecast endpoint that returns at most 7 days of
  forecast for a city.

  Scenario: Default forecast returns 7 daily entries
    Given the service is running
    And a city named "Tokyo" exists
    When a client sends GET to "/api/cities/Tokyo/weather/forecast"
    Then the response status is 200
    And the response body has a key "results" with a list of length 7

  Scenario: Forecast accepts a custom horizon up to 7 days
    Given the service is running
    And a city named "Tokyo" exists
    When a client sends GET to "/api/cities/Tokyo/weather/forecast?days=3"
    Then the response status is 200
    And the response body has a key "results" with a list of length 3

  Scenario: Forecast rejects a horizon longer than 7 days
    Given the service is running
    And a city named "Tokyo" exists
    When a client sends GET to "/api/cities/Tokyo/weather/forecast?days=8"
    Then the response status is 400
    And the response body has a key "detail" with a value containing "maximum 7 days"
