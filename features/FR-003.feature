@status-todo
Feature: FR-003 Service provides weather forecast feed
  The service publishes the weather forecast of a city as an Atom feed
  so that clients can subscribe to forecast updates with a feed reader.

  Scenario: Atom forecast feed for a city is served
    Given the service is running
    And a city named "Tokyo" exists
    And forecast records for "Tokyo" exist for the next 7 days
    When a client sends a GET request to "/api/cities/<city_uuid>/forecast/feed" for the city "Tokyo"
    Then the response status code is 200
    And the response content type is "application/atom+xml"
    And the response body is a well-formed XML document with root element "feed" in the Atom namespace "http://www.w3.org/2005/Atom"
    And the feed contains a "title" element mentioning "Tokyo"
    And the feed contains 7 "entry" elements

  Scenario: Each feed entry describes one forecast day
    Given the service is running
    And a city named "Tokyo" exists
    And forecast records for "Tokyo" exist for the next 7 days
    When a client sends a GET request to "/api/cities/<city_uuid>/forecast/feed" for the city "Tokyo"
    Then every feed entry contains a "title" element
    And every feed entry contains an "updated" element with a valid RFC 3339 timestamp
    And every feed entry contains a "summary" element mentioning "temperature"

  Scenario: Atom feed for a non-existing city returns 404
    Given the service is running
    When a client sends a GET request to "/api/cities/00000000-0000-0000-0000-000000000000/forecast/feed"
    Then the response status code is 404
