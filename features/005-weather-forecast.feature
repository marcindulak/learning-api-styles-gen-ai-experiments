@status-done
Feature: 005 Weather Forecast Feed (Atom API)
  As a client application
  I need to subscribe to weather forecast updates via Atom feed
  So that I can receive weather predictions for upcoming days

  Scenario: Retrieve 7-day weather forecast via Atom feed
    Given a city "Copenhagen" exists in the system
    And forecast data is available for the next 7 days
    When the client requests the Atom feed for "Copenhagen" forecasts
    Then the system returns HTTP 200 OK
    And the response is in Atom XML format
    And the feed contains entries for each of the next 7 days
    And each entry contains forecast date, temperature range, and conditions

  Scenario: Atom feed forecast is limited to 7 days
    Given a city "Copenhagen" exists in the system
    And forecast data is available beyond 7 days
    When the client requests the Atom feed for "Copenhagen" forecasts
    Then the response includes only the next 7 days of forecast
    And no data beyond 7 days is included
