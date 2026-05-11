@status-done
Feature: FR-004 Weather forecast Atom feed

  The service exposes the weather forecast for each registered city as an
  Atom 1.0 feed.

  Scenario: Retrieve the Atom forecast feed for an existing city
    Given the service is running
    And a city named "Tokyo" exists
    When a client sends GET to "/feeds/forecast/Tokyo"
    Then the response status is 200
    And the response Content-Type is "application/atom+xml"
    And the response body contains the substring "<feed"
    And the response body contains exactly 7 "<entry>" elements

  Scenario: Atom feed for an unknown city returns 404
    Given the service is running
    When a client sends GET to "/feeds/forecast/Atlantis"
    Then the response status is 404
