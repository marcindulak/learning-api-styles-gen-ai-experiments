@status-todo
Feature: FR-007 Weather records contain actual data
  Weather records are populated with actual data fetched from a third-party
  weather API, rather than being invented by the service.

  Scenario: Fetching weather data creates records from the third-party API
    Given the service is running
    And a city named "Tokyo" exists
    And the third-party weather API returns temperature 18.3, humidity 72, wind_speed 3.4, pressure 1008, precipitation 1.2 for the coordinates of "Tokyo"
    When the weather data fetch task runs for the city "Tokyo"
    Then a weather record for "Tokyo" exists with temperature 18.3, humidity 72, wind_speed 3.4, pressure 1008, precipitation 1.2
    And the weather record has the field "source" identifying the third-party weather API

  Scenario: Fetching forecast data creates forecast records from the third-party API
    Given the service is running
    And a city named "Tokyo" exists
    And the third-party weather API returns a 7-day forecast for the coordinates of "Tokyo"
    When the forecast data fetch task runs for the city "Tokyo"
    Then 7 forecast records for "Tokyo" exist
    And each forecast record has non-null "temperature_min" and "temperature_max" fields

  Scenario: A third-party API failure does not create weather records
    Given the service is running
    And a city named "Tokyo" exists
    And "Tokyo" has 0 weather records
    And the third-party weather API responds with status code 500
    When the weather data fetch task runs for the city "Tokyo"
    Then "Tokyo" has 0 weather records
    And the fetch task reports a failure for the city "Tokyo"
