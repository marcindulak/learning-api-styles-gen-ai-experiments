@status-todo
Feature: 003 Weather Data Storage
  The service provides weather historical data
  Weather records contain actual data from a third-party weather API

  Scenario: Store weather record for a city
    Given the service is running
    And a city "Tokyo" exists
    When a weather record is created for "Tokyo" with temperature 25.5 celsius
    Then the weather record is stored with temperature 25.5 celsius

  Scenario: Retrieve historical weather data for a city
    Given the service is running
    And a city "Delhi" exists
    And the following weather records exist for "Delhi":
      | timestamp           | temperature | humidity | pressure |
      | 2024-01-15 10:00:00 | 20.0        | 65       | 1013     |
      | 2024-01-15 11:00:00 | 21.5        | 63       | 1013     |
      | 2024-01-15 12:00:00 | 23.0        | 60       | 1012     |
    When retrieving historical weather data for "Delhi"
    Then 3 weather records are returned

  Scenario: Weather data includes common weather indicators
    Given the service is running
    And a city "Shanghai" exists
    When a weather record is created for "Shanghai" with the following data:
      | temperature | humidity | pressure | wind_speed | precipitation |
      | 18.5        | 70       | 1015     | 12.5       | 0.0           |
    Then the weather record contains temperature 18.5 celsius
    And the weather record contains humidity 70 percent
    And the weather record contains pressure 1015 hPa
    And the weather record contains wind speed 12.5 km/h
    And the weather record contains precipitation 0.0 mm
