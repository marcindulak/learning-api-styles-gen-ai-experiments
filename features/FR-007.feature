@status-todo
Feature: FR-007 - Weather records contain actual data
  The service populates each city's weather records with actual readings
  fetched from an external weather data provider, rather than fabricated
  or hardcoded values. The specific provider is an implementation detail
  decided during development of this feature, not a behavior specified
  here. A stored reading is considered stale once more than 1 hour has
  passed since it was last refreshed from the provider, so that
  consumers can distinguish a live reading from one served during a
  prolonged provider outage.

  Background:
    Given the city "Tokyo" exists with uuid "11111111-1111-1111-1111-111111111111"

  Scenario: Service stores a weather record fetched from the weather data provider
    Given the weather data provider returns a reading for "Tokyo" with temperature 18.0 and condition "Cloudy"
    When the service polls the weather data provider for "Tokyo"
    Then a weather record for "Tokyo" is stored with temperature 18.0 and condition "Cloudy"
    And the stored record's source is the weather data provider

  Scenario: Existing record is kept when the weather data provider is unavailable
    Given "Tokyo" already has a stored weather record with temperature 18.0
    And the weather data provider is unavailable
    When the service polls the weather data provider for "Tokyo"
    Then the current weather record for "Tokyo" still has temperature 18.0
    And the failed poll is logged

  Scenario: Current weather API never returns data that was not sourced from the provider
    When a client sends "GET /api/cities/11111111-1111-1111-1111-111111111111/current"
    Then every returned indicator value originates from a weather record stored via the weather data provider

  Scenario: Current weather response flags a reading as stale after a prolonged provider outage
    Given "Tokyo" has a stored weather record with temperature 18.0 last refreshed 2 hours ago
    And the weather data provider has been unavailable for the last 2 hours
    When a client sends "GET /api/cities/11111111-1111-1111-1111-111111111111/current"
    Then the response status is 200
    And the response body contains "temperature" equal to 18.0
    And the response body contains "stale" equal to true

  Scenario: Current weather response does not flag a recently refreshed reading as stale
    Given "Tokyo" has a stored weather record with temperature 18.0 last refreshed 5 minutes ago
    When a client sends "GET /api/cities/11111111-1111-1111-1111-111111111111/current"
    Then the response status is 200
    And the response body contains "stale" equal to false
