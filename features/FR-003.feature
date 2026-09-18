@status-todo
Feature: FR-003 - Weather forecast feed via Atom
  The service publishes each city's 7-day weather forecast as an Atom
  feed, with one entry per forecast day.

  Background:
    Given the city "Delhi" exists with uuid "22222222-2222-2222-2222-222222222222"
    And "Delhi" has a 7-day forecast with one entry per day

  Scenario: Retrieve the Atom feed for a city's forecast
    When a client sends "GET /api/cities/22222222-2222-2222-2222-222222222222/forecast/feed.atom"
    Then the response status is 200
    And the response content type is "application/atom+xml"
    And the response body is a well-formed Atom document
    And the feed contains exactly 7 entries

  Scenario: Each Atom entry describes one forecast day
    When a client sends "GET /api/cities/22222222-2222-2222-2222-222222222222/forecast/feed.atom"
    Then each entry has a title containing that day's forecast date
    And each entry has a summary containing that day's condition and temperature range

  Scenario: Atom feed for a city that does not exist returns 404
    When a client sends "GET /api/cities/99999999-9999-9999-9999-999999999999/forecast/feed.atom"
    Then the response status is 404
