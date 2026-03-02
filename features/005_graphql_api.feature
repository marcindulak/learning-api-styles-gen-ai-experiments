@status-done
Feature: 005 GraphQL API for Weather Data
  The Weather Forecast Service exposes common weather indicators via GraphQL API.
  Users can query weather data with flexible field selection.

  Scenario: Query current weather with specific fields
    Given the service is running
    And a city "Copenhagen" exists
    And current weather data exists for "Copenhagen"
    When I send a GraphQL query
      """
      {
        currentWeather(cityName: "Copenhagen") {
          cityName
          temperature
          conditions
        }
      }
      """
    Then the GraphQL response is successful
    And the GraphQL response contains field "currentWeather.cityName" equals "Copenhagen"
    And the GraphQL response has field "currentWeather.temperature"
    And the GraphQL response has field "currentWeather.conditions"
    And the GraphQL response does not contain field "currentWeather.humidity"

  Scenario: Query forecast with date range
    Given the service is running
    And a city "Copenhagen" exists
    And forecast data exists for "Copenhagen" for the next 7 days
    When I send a GraphQL query
      """
      {
        forecast(cityName: "Copenhagen", days: 3) {
          forecastDate
          temperature
          conditions
        }
      }
      """
    Then the GraphQL response is successful
    And the GraphQL response contains a list "forecast" with 3 items

  Scenario: Query multiple cities in one request
    Given the service is running
    And cities "Copenhagen", "Tokyo" exist
    And current weather data exists for all cities
    When I send a GraphQL query
      """
      {
        copenhagen: currentWeather(cityName: "Copenhagen") {
          temperature
        }
        tokyo: currentWeather(cityName: "Tokyo") {
          temperature
        }
      }
      """
    Then the GraphQL response is successful
    And the GraphQL response has field "copenhagen.temperature"
    And the GraphQL response has field "tokyo.temperature"
