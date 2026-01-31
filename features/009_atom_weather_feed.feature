@status-done
Feature: 009 - Weather Forecast Atom Feed

  As a user of the Weather Forecast Service
  I want to subscribe to weather forecast feeds via Atom
  So that I can receive weather updates through feed readers

  Background:
    Given the Weather Forecast Service is running
    And a city "Tokyo" exists in the system

  Scenario: Get Atom feed for a city's weather forecast
    When I request the Atom feed for city "Tokyo"
    Then I receive a response with status code 200
    And the response content type is "application/atom+xml"
    And the Atom feed contains valid XML structure

  Scenario: Atom feed contains weather forecast entries
    When I request the Atom feed for city "Tokyo"
    Then I receive a response with status code 200
    And the Atom feed contains forecast entries
    And each entry contains a title with weather summary
    And each entry contains temperature information

  Scenario: Atom feed contains proper feed metadata
    When I request the Atom feed for city "Tokyo"
    Then I receive a response with status code 200
    And the Atom feed contains a feed title
    And the Atom feed contains an updated timestamp
    And the Atom feed contains a feed id

  Scenario: Atom feed entries have unique identifiers
    When I request the Atom feed for city "Tokyo"
    Then I receive a response with status code 200
    And each Atom feed entry has a unique id

  Scenario: Return 404 for Atom feed of non-existent city
    When I request the Atom feed for non-existent city UUID "00000000-0000-0000-0000-000000000000"
    Then I receive a response with status code 404
