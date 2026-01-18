@status-done
Feature: 006 Weather Forecast
  As an API consumer
  I want to access weather forecasts for cities
  So that I can plan ahead based on predicted weather

  Scenario: Weather forecast is limited to 7 days maximum
    Given a city "Copenhagen" exists
    And forecast data exists for Copenhagen spanning 10 days
    When I request the forecast for Copenhagen
    Then the response includes maximum 7 days of forecast data

  Scenario: Forecast data includes daily weather indicators
    Given a city "Copenhagen" exists
    And 5 days of forecast data exist for Copenhagen
    When I request the forecast for Copenhagen
    Then each forecast day includes temperature, humidity, wind_speed, and description

  Scenario: Forecast data is ordered chronologically
    Given a city "Copenhagen" exists
    And forecast data exists for Copenhagen for days 1-7
    When I request the forecast for Copenhagen
    Then the forecast days are returned in ascending chronological order

  Scenario: Forecast API is accessible via REST
    Given a city "Copenhagen" exists
    And forecast data exists for Copenhagen
    When I request the forecast via REST
    Then the response status is 200 OK
    And the response includes 7-day forecast data

  Scenario: Authenticated users can access forecast endpoints
    Given I am authenticated as a regular user
    And a city "Copenhagen" exists with forecast data
    When I request the forecast via REST with authentication
    Then the request succeeds with status 200
