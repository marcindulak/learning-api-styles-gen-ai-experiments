@status-done
Feature: 007 Weather Historical Data
  As an analyst
  I need to query historical weather data
  So that I can analyze weather patterns and trends

  Scenario: Retrieve historical weather data for a city
    Given a city "Copenhagen" exists in the system
    And historical weather records exist from 2023-01-01 to 2023-12-31
    When the client requests historical weather data for "Copenhagen" from 2023-01-01 to 2023-12-31
    Then the system returns HTTP 200 OK
    And the response contains weather records with date, temperature, humidity, pressure, and wind speed
    And the records are sorted by date in ascending order

  Scenario: Filter historical data by date range
    Given a city "Copenhagen" exists with multiple historical weather records
    When the client requests historical data for a specific month (2023-06-01 to 2023-06-30)
    Then only records from June 2023 are returned
    And all records in the response are within the requested date range
