@status-todo
Feature: 003 Weather Data Storage
  As a weather service operator
  I want to store current weather, historical data, and forecasts
  So that users can access weather information

  Scenario: Store current weather for a city
    Given I am authenticated as admin
    And a city exists with name "Tokyo"
    When I store current weather for "Tokyo" with:
      | temperature | 25.5 |
      | humidity    | 60   |
      | pressure    | 1013 |
      | wind_speed  | 5.2  |
    Then the response status code is 201

  Scenario: Retrieve historical weather data
    Given I am authenticated as admin
    And current weather data exists for "London"
    When I send a GET request to "/api/weather/historical?city_name=London"
    Then the response status code is 200
    And the response contains weather data

  Scenario: Store forecast within 7-day limit
    Given I am authenticated as admin
    And a city exists with name "Paris"
    When I store a 5-day forecast for "Paris"
    Then the response status code is 201

  Scenario: Reject forecast beyond 7-day limit
    Given I am authenticated as admin
    And a city exists with name "Berlin"
    When I store a forecast for "Berlin" for 10 days from now
    Then the response status code is 400
