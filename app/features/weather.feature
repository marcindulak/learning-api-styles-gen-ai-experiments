# Feature: Weather Data Management
# Test weather records, forecasts, and alerts

Feature: Weather Data Management
  As a user of the Weather Forecast Service
  I want to access weather data
  So that I can see current conditions and forecasts

  Scenario: Get weather records for a city
    Given a city "Tokyo" exists in "Japan"
    And weather records exist for "Tokyo"
    When I request weather records for "Tokyo"
    Then I get weather data with temperature readings

  Scenario: Filter weather records by date range
    Given a city "Delhi" exists in "India"
    And weather records exist for the last 7 days
    When I request weather records from 3 days ago to today
    Then I get weather data for the requested period

  Scenario: Get 7-day forecast for a city
    Given a city "Shanghai" exists in "China"
    And 7-day forecasts exist for "Shanghai"
    When I request forecasts for "Shanghai"
    Then I get 7 forecast entries
    And each forecast has temperature high and low

  Scenario: Reject forecast beyond 7 days
    Given a city "São Paulo" exists in "Brazil"
    And I am an admin user
    When I try to create a forecast for 8 days from now
    Then I get a 400 Bad Request error
    And the error mentions "7 days"

  Scenario: Weather record has required fields
    Given a city "Mexico City" exists in "Mexico"
    When I create a weather record for "Mexico City"
    Then the record contains:
      | field       |
      | temperature |
      | humidity    |
      | wind_speed  |
      | description |

  Scenario: Forecast validation at API level
    Given I am an admin user
    And a city "Tokyo" exists
    When I try to create a forecast with forecast_date 30 days ahead
    Then the API validation rejects it
    And the response status is 400
