@status-done
Feature: 007 Weather Forecast Feed (Atom)
  The service provides weather forecast feed using Atom format
  allowing users to subscribe to weather updates

  Scenario: Retrieve Atom feed for weather forecasts
    Given the service is running
    And a city "Tokyo" exists
    And a weather forecast exists for "Tokyo" for the next 7 days
    When requesting Atom feed from "/api/feed/forecast"
    Then the response is valid Atom XML
    And the feed contains entries for city "Tokyo"

  Scenario: Atom feed contains required elements
    Given the service is running
    And a city "Delhi" exists
    And a weather forecast exists for "Delhi" for the next 3 days
    When requesting Atom feed from "/api/feed/forecast"
    Then the Atom feed contains a title element
    And the Atom feed contains updated timestamp
    And the Atom feed contains author information
    And each entry contains title, link, and summary

  Scenario: Atom feed updates when new forecast is available
    Given the service is running
    And a city "Shanghai" exists
    And the Atom feed was last updated at "2024-01-15 10:00:00"
    When a new weather forecast is created for "Shanghai"
    And requesting Atom feed from "/api/feed/forecast"
    Then the Atom feed updated timestamp is after "2024-01-15 10:00:00"
