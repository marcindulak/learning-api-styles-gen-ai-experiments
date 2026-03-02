@status-done
Feature: 007 Weather Forecast Atom Feed
  The Weather Forecast Service provides weather forecast data as an Atom feed.
  Users can subscribe to feeds for specific cities.

  Scenario: Retrieve Atom feed for a city
    Given the service is running
    And a city "Copenhagen" exists
    And forecast data exists for "Copenhagen" for the next 7 days
    When I send a GET request to "/feeds/forecast/Copenhagen"
    Then the response status code is 200
    And the response Content-Type is "application/atom+xml"
    And the feed contains 7 entries
    And each entry has a title, updated date, and content

  Scenario: Atom feed entry contains forecast details
    Given the service is running
    And a city "Copenhagen" exists
    And forecast data exists for "Copenhagen" for the next 7 days
    When I send a GET request to "/feeds/forecast/Copenhagen"
    Then the response status code is 200
    And the first entry contains forecast date in the title
    And the first entry content includes temperature
    And the first entry content includes conditions

  Scenario: Atom feed for non-existent city returns 404
    Given the service is running
    When I send a GET request to "/feeds/forecast/NonExistentCity"
    Then the response status code is 404

  Scenario: Atom feed includes proper metadata
    Given the service is running
    And a city "Copenhagen" exists
    And forecast data exists for "Copenhagen" for the next 7 days
    When I send a GET request to "/feeds/forecast/Copenhagen"
    Then the response status code is 200
    And the feed has a title containing "Copenhagen"
    And the feed has a link to itself
    And the feed has an updated timestamp
