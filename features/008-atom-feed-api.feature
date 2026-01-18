@status-done
Feature: 008 Atom Feed API
  As an API consumer
  I want to access weather forecast data via Atom feed
  So that I can subscribe to weather updates in feed readers

  Scenario: Atom feed is accessible via HTTP GET
    Given forecast data exists for multiple cities
    When I request the Atom feed endpoint
    Then the response status is 200 OK
    And the response is valid Atom XML

  Scenario: Atom feed contains weather forecast entries
    Given forecast data exists for Copenhagen and Tokyo
    When I request the Atom feed endpoint
    Then the feed includes entries for both cities
    And each entry contains forecast information

  Scenario: Atom feed entries include required fields
    Given forecast data exists for Copenhagen
    When I request the Atom feed endpoint
    Then each entry includes title, updated timestamp, and content
    And the feed includes updated timestamp

  Scenario: Atom feed is valid XML
    Given forecast data exists
    When I request the Atom feed endpoint
    Then the response is well-formed XML
    And the XML includes valid Atom namespace

  Scenario: Atom feed is accessible to unauthenticated users
    Given no JWT token is provided
    And forecast data exists
    When I request the Atom feed endpoint
    Then the request succeeds with status 200 OK
