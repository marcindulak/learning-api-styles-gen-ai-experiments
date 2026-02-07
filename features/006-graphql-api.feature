@status-done
Feature: 006 GraphQL API for Weather Indicators
  The service exposes common weather indicators via GraphQL API
  allowing flexible queries and mutations

  Scenario: Query cities via GraphQL
    Given the service is running
    And a city "Tokyo" exists
    When executing GraphQL query:
      """
      {
        cities {
          name
          country
        }
      }
      """
    Then the GraphQL response contains city "Tokyo"

  Scenario: Query specific city by name via GraphQL
    Given the service is running
    And a city "Delhi" with country "India" exists
    When executing GraphQL query:
      """
      {
        city(name: "Delhi") {
          name
          country
          latitude
          longitude
        }
      }
      """
    Then the GraphQL response contains city "Delhi" with country "India"

  Scenario: Query weather data via GraphQL
    Given the service is running
    And a city "Shanghai" exists
    And a weather record exists for "Shanghai" with temperature 20.0 celsius
    When executing GraphQL query:
      """
      {
        weatherData(city: "Shanghai") {
          temperature
          humidity
          pressure
        }
      }
      """
    Then the GraphQL response contains temperature 20.0
