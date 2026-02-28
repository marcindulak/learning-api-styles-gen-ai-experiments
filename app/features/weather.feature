Feature: Weather records and forecasts
  As a user of the Weather Forecast Service
  I want to view and manage weather data
  So that I can track weather conditions

  Scenario: Create a weather record as admin
    Given I am authenticated as admin
    And a test city exists
    When I POST a weather record for the test city
    Then the response status is 201

  Scenario: List weather records for a city
    Given a test city exists with weather records
    When I GET weather records for the test city
    Then the response status is 200
    And the response contains weather records

  Scenario: Create a forecast as admin
    Given I am authenticated as admin
    And a test city exists
    When I POST a forecast for the test city
    Then the response status is 201

  Scenario: Forecast date must be within 7 days
    Given I am authenticated as admin
    And a test city exists
    When I POST a forecast with a date more than 7 days out
    Then the response status is 400

  Scenario: High temperature must be >= low temperature
    Given I am authenticated as admin
    And a test city exists
    When I POST a forecast with high temp less than low temp
    Then the response status is 400
