@status-todo
Feature: 003 Weather Data Storage
  As a service
  I want to store weather data in a database
  So that I can provide historical weather information

  Scenario: Weather data is stored with timestamp and city reference
    Given a city "Copenhagen" exists
    When I store weather data for Copenhagen with temperature 15.5, humidity 65, wind_speed 10.2, and timestamp
    Then the weather data is persisted in the database
    And the weather record has a reference to Copenhagen

  Scenario: Multiple weather records can be stored for the same city
    Given a city "Copenhagen" exists
    When I store 3 separate weather records for Copenhagen with different timestamps
    Then all 3 records are stored in the database
    And all records reference Copenhagen

  Scenario: Weather data includes valid weather indicators
    Given a city "Copenhagen" exists
    When I store weather data with temperature, humidity, wind_speed, pressure, and description
    Then all weather indicators are persisted
    And the weather record is retrievable with all indicators

  Scenario: Oldest weather data can be queried for historical analysis
    Given a city "Copenhagen" exists
    And multiple weather records exist for Copenhagen spanning 30 days
    When I query historical weather data for Copenhagen
    Then I receive all historical records in chronological order
