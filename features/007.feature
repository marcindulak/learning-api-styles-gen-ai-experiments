@status-todo
Feature: 007 Weather Forecast Atom Feed
  As a weather service user
  I want to subscribe to weather forecast feeds
  So that I can receive updates in a standard feed format

  Scenario: Retrieve Atom feed for city forecast
    Given forecast data exists for "Copenhagen" for the next 7 days
    When I send a GET request to "/feeds/forecast/Copenhagen/"
    Then the response status code is 200
    And the Content-Type is "application/atom+xml"

  Scenario: Atom feed contains forecast entries
    Given forecast data exists for "Tokyo" for the next 5 days
    When I send a GET request to "/feeds/forecast/Tokyo/"
    Then the response status code is 200
    And the feed contains 5 entries

  Scenario: Return 404 for non-existent city feed
    When I send a GET request to "/feeds/forecast/NonExistentCity/"
    Then the response status code is 404

  Scenario: Atom feed includes required metadata
    Given forecast data exists for "London"
    When I send a GET request to "/feeds/forecast/London/"
    Then the response status code is 200
    And the feed contains a title "Weather Forecast for London"
    And the feed contains updated timestamp
